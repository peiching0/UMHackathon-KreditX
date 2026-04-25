"""
llm_engine.py — Kredit67 AI Engine
"""
import json
import re
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a credit analyst helping unbanked Malaysian micro-business owners get small loans. Treat all informal evidence (WhatsApp chats, photos, handwritten records) as valid.

SCORING (100 pts total, QUALIFIED if >= 55):
1. Business Stability (0-25): years operating, repeat customers, consistency
2. Financial Health (0-25): net monthly income = daily_sales*30 - expenses, inventory size
3. Loan Purpose (0-20): productive use, reasonable amount vs income
4. Evidence Quality (0-20): real transactions, photos, chat records shown
5. Repayment Capacity (0-10): monthly repayment should be under 40% of net income

LOAN SCHEMES (pick best match):
- TEKUN Nasional: up to RM50k, Bumiputera businesses
- AIM Amanah Ikhtiar: RM1k-RM20k, rural women
- BSN MyKredit: RM1k-RM10k, easy approval
- Agrobank Agro-Emas: up to RM50k, food/agri
- SME Bank Micro Finance: up to RM50k, general

Reply ONLY with this JSON, no markdown:
{"credit_score":<0-100>,"decision":"QUALIFIED or NOT QUALIFIED","score_breakdown":{"business_stability":{"score":<0-25>,"reason":"<1 sentence>"},"financial_health":{"score":<0-25>,"reason":"<1 sentence>"},"loan_purpose":{"score":<0-20>,"reason":"<1 sentence>"},"evidence_quality":{"score":<0-20>,"reason":"<1 sentence>"},"repayment_capacity":{"score":<0-10>,"reason":"<1 sentence>"}},"loan_recommendation":{"approved_amount_min":<int or null>,"approved_amount_max":<int or null>,"recommended_scheme":"<name or null>","interest_rate_pct":<float or null>,"repayment_months":<int or null>,"monthly_repayment_rm":<int or null>},"improvement_tips":["<tip1 if not qualified else empty>","<tip2>","<tip3>"],"come_back_in":"<e.g. 3-6 months or null>","summary":"<2 sentences, warm tone>","encouraging_message":"<1 uplifting sentence>"}
"""


def _build_user_message(applicant_data: dict, evidence_texts: list) -> str:
    d = applicant_data
    daily_sales           = float(d.get("daily_sales", 0))
    monthly_income        = daily_sales * 30
    monthly_expenses      = float(d.get("monthly_expenses", 0))
    net_income            = monthly_income - monthly_expenses
    inventory_value       = float(d.get("inventory_value", 0))
    loan_amount           = float(d.get("loan_amount_required", 0))
    est_monthly_repayment = (loan_amount / 36) * 1.04 if loan_amount > 0 else 0
    ratio = (
        f"{(est_monthly_repayment / net_income * 100):.1f}%"
        if net_income > 0 else "N/A (no income data)"
    )

    msg = f"""
APPLICANT PROFILE
-----------------------------------------
Business Name    : {d.get('business_name', 'N/A')}
Business Type    : {d.get('business_type', 'N/A')}
State            : {d.get('state', 'N/A')}
Years Operating  : {d.get('years_operating', 'N/A')}

FINANCIALS
-----------------------------------------
Daily Sales (est.)       : RM {daily_sales:,.2f}
Estimated Monthly Income : RM {monthly_income:,.2f}
Monthly Expenses         : RM {monthly_expenses:,.2f}
Net Monthly Income       : RM {net_income:,.2f}
Inventory Value          : RM {inventory_value:,.2f}

LOAN REQUEST
-----------------------------------------
Amount Required          : RM {loan_amount:,.2f}
Reason for Loan          : {d.get('loan_reason', 'N/A')}
Est. Monthly Repayment   : RM {est_monthly_repayment:,.2f} (36 months @ ~4%)
Repayment-to-Income Ratio: {ratio}
"""
    if evidence_texts:
        msg += f"\nINFORMAL EVIDENCE PROVIDED ({len(evidence_texts)} source(s))\n"
        msg += "-----------------------------------------\n"
        for i, text in enumerate(evidence_texts, 1):
            trimmed = text.strip()[-2000:]
            msg += f"[Evidence {i}]\n{trimmed}\n\n"
    else:
        msg += "\nNo text evidence provided.\n"

    msg += (
        "\nAnalyse all the above information and any images provided. "
        "Return your assessment as a JSON object following the exact format in your instructions."
    )
    return msg.strip()


def assess_loan_eligibility(
    applicant_data: dict,
    evidence_texts: list = None,
    evidence_images: list = None,
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY in .env file"}

    evidence_texts  = evidence_texts  or []
    evidence_images = evidence_images or []

    user_text = SYSTEM_PROMPT + "\n\n" + _build_user_message(applicant_data, evidence_texts)
    parts = [user_text]

    for media_type, raw_bytes in evidence_images:
        parts.append(types.Part.from_bytes(data=raw_bytes, mime_type=media_type))

    print(f"Sending to Gemini — {len(evidence_texts)} text(s), {len(evidence_images)} image(s)...")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=parts,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=8192,
            ),
        )
        print("Gemini responded successfully")
    except Exception as e:
        print(f"Gemini failed: {e}")
        return {"error": "Gemini API call failed", "details": str(e)}

    try:
        raw_text = response.text.strip()
    except Exception as e:
        return {"error": "Empty or blocked response from Gemini", "details": str(e)}

    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from Gemini", "raw_output": raw_text}

    return result


if __name__ == "__main__":
    sample_applicant = {
        "business_name": "Siti's Home Bakery",
        "business_type": "Home-based bakery",
        "state": "Selangor",
        "years_operating": "2 years",
        "daily_sales": 85,
        "monthly_expenses": 1100,
        "inventory_value": 600,
        "loan_amount_required": 5000,
        "loan_reason": "Buy a new industrial oven to increase daily production",
    }
    sample_chat = """
Customer: Kak boleh order 3 dozen kuih raya? - 3 Apr
Siti: Boleh! RM45 total, bayar dulu ya
Customer: Transfer dah. Terima kasih!
April Week 1 total sales: RM 680
"""
    result = assess_loan_eligibility(
        applicant_data=sample_applicant,
        evidence_texts=[sample_chat],
        evidence_images=[],
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    #updated_last