"""
kreditX.py — Kredit67 FastAPI Backend
Run: uvicorn kreditX:app --reload --port 9000
"""
import asyncio
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from typing import Optional, List
from llm_engine import assess_loan_eligibility
from database import ReportDB
import random, string
from datetime import datetime

app = FastAPI(
    title="KreditX — AI Loan Assessment API",
    description="Micro-loan eligibility scoring for unbanked rural entrepreneurs in Malaysia.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB singleton ──────────────────────────────────────────────────────────────
db = ReportDB()


def _gen_report_id():
    return "RPT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def _generate_pdf(result, form_data, report_id):
    """Generate PDF bytes. Falls back to plain text if reportlab missing."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from io import BytesIO

        GREEN_DARK  = colors.HexColor("#0d4a24")
        GREEN_MID   = colors.HexColor("#1a7a3c")
        GREEN_LIGHT = colors.HexColor("#e8f5ed")
        RED         = colors.HexColor("#b91c1c")
        GRAY        = colors.HexColor("#888888")

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)

        h1   = ParagraphStyle("h1",   fontName="Helvetica-Bold", fontSize=22, textColor=GREEN_DARK, spaceAfter=4)
        h2   = ParagraphStyle("h2",   fontName="Helvetica-Bold", fontSize=13, textColor=GREEN_DARK, spaceBefore=12, spaceAfter=4)
        body = ParagraphStyle("body", fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#1a1a1a"), spaceAfter=4, leading=14)
        sm   = ParagraphStyle("sm",   fontName="Helvetica",      fontSize=8,  textColor=GRAY)
        ctr  = ParagraphStyle("ctr",  fontName="Helvetica-Bold", fontSize=28, textColor=GREEN_MID, alignment=1)

        decision = result.get("decision", "—")
        score    = result.get("credit_score", 0)
        rec      = result.get("loan_recommendation", {})
        bd       = result.get("score_breakdown", {})
        tips     = result.get("improvement_tips", [])
        now      = datetime.now().strftime("%d %b %Y, %H:%M")

        story = []
        story.append(Paragraph("💰 KreditX", h1))
        story.append(Paragraph("AI-Powered Micro-Loan Assessment Report", ParagraphStyle("sub", fontName="Helvetica", fontSize=11, textColor=GREEN_MID, spaceAfter=2)))
        story.append(Paragraph(f"Report ID: {report_id}  |  Generated: {now}", sm))
        story.append(HRFlowable(width="100%", thickness=2, color=GREEN_DARK, spaceAfter=12))

        d_color = GREEN_MID if decision == "QUALIFIED" else RED
        story.append(Paragraph(decision, ParagraphStyle("dec", fontName="Helvetica-Bold", fontSize=16, textColor=d_color, alignment=1, spaceBefore=6, spaceAfter=2)))
        story.append(Paragraph(str(score), ctr))
        story.append(Paragraph("CREDIT SCORE / 100", ParagraphStyle("sl", fontName="Helvetica-Bold", fontSize=9, textColor=GREEN_MID, alignment=1, spaceAfter=8)))

        if result.get("summary"):
            story.append(Paragraph("AI Summary", h2))
            story.append(Paragraph(result["summary"], body))
        if result.get("encouraging_message"):
            story.append(Paragraph(f'"{result["encouraging_message"]}"', ParagraphStyle("enc", fontName="Helvetica-Oblique", fontSize=10, textColor=GREEN_DARK, spaceAfter=8, leftIndent=10)))

        story.append(Paragraph("Applicant Information", h2))
        info_data = [
            ["Business Name",    form_data.get("biz_name","—")],
            ["Business Type",    form_data.get("biz_type","—")],
            ["State",            form_data.get("state","—")],
            ["Years Operating",  str(form_data.get("years","—"))],
            ["Daily Sales",      f"RM {float(form_data.get('daily_sales',0)):,.2f}"],
            ["Monthly Expenses", f"RM {float(form_data.get('monthly_exp',0)):,.2f}"],
            ["Loan Requested",   f"RM {float(form_data.get('loan_amount',0)):,.2f}"],
            ["Loan Reason",      form_data.get("reason","—")],
        ]
        t = Table(info_data, colWidths=[60*mm, 110*mm])
        t.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),"Helvetica"), ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9), ("TEXTCOLOR",(0,0),(0,-1),GRAY),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, GREEN_LIGHT]),
            ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#e8e8e8")), ("PADDING",(0,0),(-1,-1),5),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))

        if bd:
            story.append(Paragraph("Credit Score Breakdown", h2))
            bd_labels = {
                "business_stability": ("Business Stability", 25),
                "financial_health":   ("Financial Health",   25),
                "loan_purpose":       ("Loan Purpose",       20),
                "evidence_quality":   ("Evidence Quality",   20),
                "repayment_capacity": ("Repayment Capacity", 10),
            }
            bd_data = [["Factor", "Score", "Reason"]]
            for key, (label, mx) in bd_labels.items():
                item = bd.get(key, {})
                bd_data.append([label, f"{item.get('score',0)}/{mx}", item.get("reason","—")])
            bt = Table(bd_data, colWidths=[45*mm, 20*mm, 105*mm])
            bt.setStyle(TableStyle([
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("BACKGROUND",(0,0),(-1,0),GREEN_DARK), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, GREEN_LIGHT]),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#e8e8e8")), ("PADDING",(0,0),(-1,-1),5),
                ("ALIGN",(1,0),(1,-1),"CENTER"),
            ]))
            story.append(bt)
            story.append(Spacer(1, 8))

        if decision == "QUALIFIED" and rec:
            story.append(Paragraph("Loan Recommendation", h2))
            rec_data = []
            if rec.get("approved_amount_min") and rec.get("approved_amount_max"):
                rec_data.append(["Approved Amount", f"RM {rec['approved_amount_min']:,} — RM {rec['approved_amount_max']:,}"])
            if rec.get("recommended_scheme"): rec_data.append(["Recommended Scheme", rec["recommended_scheme"]])
            if rec.get("interest_rate_pct"):  rec_data.append(["Interest Rate", f"{rec['interest_rate_pct']}% per year"])
            if rec.get("monthly_repayment_rm"): rec_data.append(["Monthly Repayment", f"RM {rec['monthly_repayment_rm']:,} / month"])
            if rec.get("repayment_months"):   rec_data.append(["Repayment Period", f"{rec['repayment_months']} months"])
            if rec_data:
                rt = Table(rec_data, colWidths=[60*mm, 110*mm])
                rt.setStyle(TableStyle([
                    ("FONTNAME",(0,0),(-1,-1),"Helvetica"), ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
                    ("FONTSIZE",(0,0),(-1,-1),9), ("TEXTCOLOR",(0,0),(0,-1),GRAY),
                    ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, GREEN_LIGHT]),
                    ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#e8e8e8")), ("PADDING",(0,0),(-1,-1),5),
                ]))
                story.append(rt)

        valid_tips = [t for t in tips if t]
        if valid_tips:
            story.append(Paragraph("Steps to Improve", h2))
            for i, tip in enumerate(valid_tips, 1):
                story.append(Paragraph(f"{i}. {tip}", body))

        if result.get("come_back_in"):
            story.append(Paragraph(f"Recommended to reapply in: {result['come_back_in']}", ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#A46034"), spaceAfter=4)))

        story.append(HRFlowable(width="100%", thickness=1, color=GREEN_LIGHT, spaceBefore=12, spaceAfter=4))
        story.append(Paragraph("This report is generated by KreditX AI. For reference only — not a formal credit approval.", sm))

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        lines = [
            "KREDITX AI LOAN ASSESSMENT REPORT", "="*50,
            f"Report ID: {report_id}",
            f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
            f"DECISION: {result.get('decision','—')}",
            f"CREDIT SCORE: {result.get('credit_score','—')}/100",
            f"BUSINESS: {form_data.get('biz_name','—')}",
            f"SUMMARY: {result.get('summary','')}",
        ]
        return "\n".join(lines).encode("utf-8")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def home():
    return {"status": "ok", "message": "KreditX API is running"}


# ── Main assessment endpoint ──────────────────────────────────────────────────

@app.post("/evaluate-loan", tags=["Loan Assessment"])
async def evaluate_loan(
    biz_name:        str   = Form(...),
    biz_type:        str   = Form(...),
    biz_state:       str   = Form(...),
    biz_year:        int   = Form(...),
    fin_sales:       float = Form(...),
    fin_expenses:    float = Form(...),
    fin_inventory:   float = Form(...),
    loan_amount:     float = Form(...),
    reason:          str   = Form(...),
    voice_text:      str   = Form(default=""),
    evidence_images: List[UploadFile] = File(default=[]),
):
    if fin_sales <= 0:
        raise HTTPException(status_code=422, detail="fin_sales must be greater than 0")
    if loan_amount <= 0:
        raise HTTPException(status_code=422, detail="loan_amount must be greater than 0")

    applicant_data = {
        "business_name":        biz_name,
        "business_type":        biz_type,
        "state":                biz_state,
        "years_operating":      biz_year,
        "daily_sales":          fin_sales,
        "monthly_expenses":     fin_expenses,
        "inventory_value":      fin_inventory,
        "loan_amount_required": loan_amount,
        "loan_reason":          reason,
    }

    form_data_for_db = {
        "biz_name":   biz_name,  "biz_type":  biz_type,
        "state":      biz_state, "years":     biz_year,
        "daily_sales":fin_sales, "monthly_exp":fin_expenses,
        "inventory":  fin_inventory, "loan_amount": loan_amount,
        "reason":     reason,    "voice_text": voice_text,
    }

    evidence_texts = [voice_text.strip()] if voice_text and voice_text.strip() else []

    evidence_images_list = []
    for img in evidence_images:
        if img and img.filename:
            image_bytes = await img.read()
            if image_bytes:
                evidence_images_list.append((img.content_type or "image/jpeg", image_bytes))

    print(f"Request — {biz_name} | RM{loan_amount:,.0f} | {len(evidence_texts)} texts | {len(evidence_images_list)} images")

    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: assess_loan_eligibility(applicant_data, evidence_texts, evidence_images_list)
            ),
            timeout=130,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Assessment timed out. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    if "error" in result:
        raise HTTPException(status_code=500, detail=result)

    # ── Generate report ID + PDF then save to DB ──────────────────────────────
    report_id = _gen_report_id()
    pdf_bytes = _generate_pdf(result, form_data_for_db, report_id)

    try:
        db.save_report(report_id, pdf_bytes, form_data_for_db, result)
        print(f"✅ Saved to DB — {report_id} | {result.get('decision')} | score {result.get('credit_score')}")
    except Exception as e:
        print(f"⚠️ DB save failed (continuing): {e}")

    # Return result + report_id to frontend
    result["report_id"] = report_id
    print(f"Done — {report_id} | score: {result.get('credit_score')} | {result.get('decision')}")
    return JSONResponse(content=result)


# ── Stakeholder: get report by ID ─────────────────────────────────────────────

@app.get("/report/{report_id}", tags=["Stakeholder"])
def get_report(report_id: str):
    """Returns full report metadata (no PDF blob) for stakeholder dashboard."""
    data = db.get_metadata(report_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")
    return JSONResponse(content=data)


@app.get("/report/{report_id}/pdf", tags=["Stakeholder"])
def get_report_pdf(report_id: str):
    """Returns the raw PDF file for download."""
    pdf = db.get_pdf(report_id)
    if not pdf:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=kreditx_{report_id}.pdf"}
    )


@app.get("/reports", tags=["Stakeholder"])
def list_reports(limit: int = 50):
    """List all reports newest first — for stakeholder dashboard overview."""
    return JSONResponse(content=db.list_reports(limit))


@app.get("/stats", tags=["Stakeholder"])
def get_stats():
    """Aggregate stats — total, qualified count, avg score."""
    return JSONResponse(content=db.stats())

#updated_last