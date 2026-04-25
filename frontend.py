import streamlit as st
import time
import random
import string
import requests
from datetime import datetime
from io import BytesIO

BACKEND_URL = "http://localhost:9000"

st.set_page_config(page_title="KreditX", page_icon="💰", layout="centered", initial_sidebar_state="collapsed")

lang = {
    "EN": {
        "stakeholders_login": "STAKEHOLDER LOGIN", "user_form": "User Details",
        "stakeholder_dashboard": "Stakeholder Dashboard", "copyright": "© 2026 KreditX",
        "ai_badge": "AI-Powered Credit Assessment", "welcome_title": "Welcome!",
        "welcome_sub": "Tell us about your business! We assess your real business potential.",
        "start_btn": "Start Free",
        "agree": "Do you agree to share your business information with stakeholders?",
        "login_title": "Login to Stakeholder Dashboard!",
        "email": "Email", "password": "Password", "login_btn": "Login",
        "step1": "Your Details", "step2": "Summary", "step3": "Result",
        "voice_sub": "Tell us about your business. Speak in any local dialect • Auto-translated",
        "biz_info": "BUSINESS INFORMATION", "biz_name": "BUSINESS NAME",
        "biz_type": "BUSINESS TYPE", "biz_state": "STATE", "biz_year": "YEARS OPERATING",
        "biz_name_ph": "eg. Kedai ABC",
        "fin_info": "FINANCE DETAILS", "fin_sales": "DAILY SALES (RM)",
        "fin_expenses": "MONTHLY EXPENSES (RM)", "fin_inventory": "INVENTORY VALUE (RM)",
        "upload_photo": "📸 Upload Evidence Photos",
        "upload_photo_sub": "WhatsApp screenshots, stall photos, receipts — upload multiple!",
        "voice_evidence": "CHAT / VOICE EVIDENCE",
        "voice_evidence_ph": "Paste WhatsApp chat here, or describe your business...",
        "loan_amount": "Loan Amount Required (RM)", "reason": "REASON FOR LOAN",
        "submit": "SUBMIT",
        "summary_title": "Summary of Information Received",
        "biz_name_lbl": "Business Name", "biz_type_lbl": "Business Type",
        "biz_state_lbl": "State", "fin_sales_lbl": "Daily Sales",
        "fin_expenses_lbl": "Monthly Expenses", "fin_inventory_lbl": "Inventory Value",
        "documents": "Photos Uploaded", "loan_lbl": "Loan Amount Required",
        "info_confirm": "Information Correct?", "yes_btn": "Yes — See Result", "no_btn": "No, Edit",
        "loading_title": "AI is Evaluating Your Details....",
        "loading_sub": "This takes 20-60 seconds. Please don't close this page.",
        "eligible": "✅ Eligible for a Loan",
        "sub_title": "Congratulations, {}! Loan Qualified.",
        "download_PDF": "⬇ Download PDF Report",
        "credit_score": "YOUR CREDIT SCORE", "good_score": "GOOD",
        "factors": "CREDIT FACTORS", "loan_range": "RECOMMENDED LOAN AMOUNT",
        "rate": "INTEREST RATE", "monthly_pay": "ESTIMATED MONTHLY PAYMENT",
        "bank": "RECOMMENDED SCHEME",
        "not_eligible": "❌ Not Eligible for a Loan",
        "not_sub_title": "Don't Give Up! Follow This Guide",
        "again": "Try Again", "current_score": "CURRENT CREDIT SCORE",
        "user_score": "Your Score", "required_score": "Required Score",
        "max_score": "Maximum Score",
        "retry_note": "❗Try again after completing the steps below",
        "step_improve": "STEPS TO IMPROVE — START NOW!",
        "download_PDF_btn": "⬇ Download Improvement Guide PDF",
        "dashboard_title": "Stakeholder Dashboard",
        "enter": "Enter Report ID", "view_report": "View Report",
        "applicant": "New Applicant", "gen_report": "Report generated on",
        "back_btn": "BACK", "download_btn": "⬇ Download Report PDF",
        "factors_lbl": "CREDIT FACTORS", "summary_ai": "AI SUMMARY",
        "encouraging": "MESSAGE", "come_back": "Come Back In",
        "biz_types": ["Food & Beverage", "Handicraft", "Home-based Bakeries", "Agriculture", "Retail", "Services", "Others"],
        "biz_states": ["Johor","Kedah","Kelantan","Malacca","Negeri Sembilan","Pahang","Perak","Perlis","Penang","Sabah","Sarawak","Selangor","Terengganu","W.P. Kuala Lumpur","W.P. Labuan","W.P. Putrajaya"],
    },
    "BM": {
        "stakeholders_login": "LOG MASUK PIHAK BERKEPENTINGAN", "user_form": "Maklumat Pengguna",
        "stakeholder_dashboard": "Papan Pemuka", "copyright": "© 2026 ",
        "ai_badge": "Penilaian Kredit Berasaskan AI", "welcome_title": "Selamat Datang!",
        "welcome_sub": "Ceritakan tentang perniagaan anda! Kami menilai potensi sebenar perniagaan anda.",
        "start_btn": "Mula Percuma",
        "agree": "Adakah anda bersetuju berkongsi maklumat perniagaan anda?",
        "login_title": "Log Masuk ke Papan Pemuka!",
        "email": "E-mel", "password": "Kata Laluan", "login_btn": "Log Masuk",
        "step1": "Maklumat Anda", "step2": "Ringkasan", "step3": "Keputusan",
        "voice_sub": "Ceritakan tentang perniagaan anda dalam mana-mana dialek • Terjemahan automatik",
        "biz_info": "MAKLUMAT PERNIAGAAN", "biz_name": "NAMA PERNIAGAAN",
        "biz_type": "JENIS PERNIAGAAN", "biz_state": "NEGERI", "biz_year": "TAHUN BEROPERASI",
        "biz_name_ph": "contoh: Kedai ABC",
        "fin_info": "MAKLUMAT KEWANGAN", "fin_sales": "JUALAN HARIAN (RM)",
        "fin_expenses": "PERBELANJAAN BULANAN (RM)", "fin_inventory": "NILAI INVENTORI (RM)",
        "upload_photo": "📸 Muat Naik Gambar Bukti",
        "upload_photo_sub": "Screenshot WhatsApp, gambar gerai, resit — boleh muat naik berbilang!",
        "voice_evidence": "BUKTI SEMBANG / SUARA",
        "voice_evidence_ph": "Tampal sembang WhatsApp di sini...",
        "loan_amount": "Jumlah Pinjaman Diperlukan (RM)", "reason": "SEBAB PINJAMAN",
        "submit": "HANTAR",
        "summary_title": "Ringkasan Maklumat Diterima",
        "biz_name_lbl": "Nama Perniagaan", "biz_type_lbl": "Jenis Perniagaan",
        "biz_state_lbl": "Negeri", "fin_sales_lbl": "Jualan Harian",
        "fin_expenses_lbl": "Perbelanjaan Bulanan", "fin_inventory_lbl": "Nilai Inventori",
        "documents": "Gambar Dimuat Naik", "loan_lbl": "Jumlah Pinjaman",
        "info_confirm": "Maklumat Betul?", "yes_btn": "Ya — Lihat Keputusan", "no_btn": "Tidak, Edit",
        "loading_title": "AI sedang menilai maklumat anda....",
        "loading_sub": "Ini mengambil masa 20-60 saat. Sila jangan tutup halaman ini.",
        "eligible": "✅ Layak untuk Pinjaman",
        "sub_title": "Tahniah, {}! Pinjaman Diluluskan.",
        "download_PDF": "⬇ Muat Turun Laporan PDF",
        "credit_score": "SKOR KREDIT ANDA", "good_score": "BAIK",
        "factors": "FAKTOR KREDIT", "loan_range": "PINJAMAN DISYORKAN",
        "rate": "KADAR FAEDAH", "monthly_pay": "ANGGARAN BAYARAN BULANAN",
        "bank": "SKIM DISYORKAN",
        "not_eligible": "❌ Tidak Layak untuk Pinjaman",
        "not_sub_title": "Jangan Putus Asa! Ikuti Panduan Ini",
        "again": "Cuba Lagi", "current_score": "SKOR KREDIT SEMASA",
        "user_score": "Skor Anda", "required_score": "Skor Diperlukan",
        "max_score": "Skor Maksimum",
        "retry_note": "❗Cuba lagi selepas melengkapkan langkah di bawah",
        "step_improve": "LANGKAH PENAMBAHBAIKAN — MULA SEKARANG",
        "download_PDF_btn": "⬇ Muat Turun Panduan PDF",
        "dashboard_title": "Papan Pemuka Pihak Berkepentingan",
        "enter": "Masukkan ID Laporan", "view_report": "Lihat Laporan",
        "applicant": "Pemohon Baharu", "gen_report": "Laporan dijana pada",
        "back_btn": "KEMBALI", "download_btn": "⬇ Muat Turun Laporan PDF",
        "factors_lbl": "FAKTOR KREDIT", "summary_ai": "RINGKASAN AI",
        "encouraging": "MESEJ", "come_back": "Cuba Semula Dalam",
        "biz_types": ["Makanan & Minuman","Kraf Tangan","Bakeri dari Rumah","Pertanian","Runcit","Perkhidmatan","Lain-lain"],
        "biz_states": ["Johor","Kedah","Kelantan","Melaka","Negeri Sembilan","Pahang","Perak","Perlis","Pulau Pinang","Sabah","Sarawak","Selangor","Terengganu","W.P. Kuala Lumpur","W.P. Labuan","W.P. Putrajaya"],
    }
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root {
    --green_dark: #0d4a24; --green_mid: #1a7a3c; --green_light: #e8f5ed;
    --white: #ffffff; --gray_100: #f5f5f5; --gray_200: #e8e8e8;
    --gray_500: #888; --red_dark: #b91c1c; --red_light: #fbe9e9;
    --text_dark: #1a1a1a; --yellow_light: #FFFBEB; --yellow_dark: #A46034;
}
.stApp { font-family: 'DM Sans', sans-serif; background-color: var(--white); color: var(--text_dark); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 1100px !important; margin: 0 auto; }
.page-wrap { padding: 20px 16px 30px; }
.ai-badge { display:inline-flex; align-items:center; gap:6px; background:var(--green_light); color:var(--green_mid); font-size:13px; font-weight:600; padding:4px 10px; border-radius:20px; margin-bottom:20px; }
.welcome-title { font-family:'DM Serif Display',serif; font-size:42px; line-height:1.1; color:var(--green_dark); margin:0 0 10px; }
.welcome-sub { font-size:16px; color:var(--text_dark); line-height:1.6; margin-bottom:24px; }
.divider { border:none; height:1px; background:var(--gray_200); margin:24px 0; }
.section-label { font-size:15px; font-weight:700; letter-spacing:1px; color:var(--green_dark); margin:18px 0 8px; text-transform:uppercase; }
.stepper { display:flex; align-items:flex-start; justify-content:center; gap:0; margin:24px 0 2px; }
.step-item { display:flex; flex-direction:column; align-items:center; flex:1; }
.step-circle { width:28px; height:28px; border-radius:50%; background:var(--gray_200); color:var(--gray_500); display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; }
.step-circle.active { background:var(--green_dark); color:var(--white); }
.step-circle.done { background:var(--green_mid); color:var(--white); }
.step-label { font-size:10px; color:var(--gray_500); margin-top:4px; text-align:center; }
.step-label.active { color:var(--green_dark); font-weight:600; }
.step-line { flex:1; height:2px; background:var(--gray_200); margin-top:14px; margin-left:-4px; margin-right:-4px; }
.step-line.done { background:var(--green_mid); }
.card { background:var(--white); border-radius:14px; border:1px solid var(--gray_200); padding:18px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
.summary-row { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid var(--gray_100); font-size:13px; }
.summary-row:last-child { border-bottom:none; }
.summary-key { color:var(--gray_500); flex:1; }
.summary-val { font-weight:600; color:var(--text_dark); text-align:right; flex:1; }
.score-ring-wrap { text-align:center; padding:16px 0; }
.score-num { font-size:64px; font-weight:800; color:var(--green_mid); line-height:1; }
.score-denom { font-size:18px; color:var(--gray_500); }
.score-label { font-size:13px; font-weight:600; color:var(--green_mid); letter-spacing:1px; margin-top:4px; }
.loan-box { border:2px solid var(--green_dark); border-radius:10px; padding:14px; margin-bottom:10px; }
.loan-box-label { font-size:10px; font-weight:700; letter-spacing:1px; color:var(--green_dark); margin-bottom:4px; }
.loan-box-val { font-size:22px; font-weight:800; color:var(--green_dark); }
.eligible-badge { background:var(--green_light); border:2px solid var(--green_dark); color:var(--green_dark); border-radius:10px; font-size:15px; font-weight:700; padding:8px 12px; text-align:center; }
.not-eligible-badge { background:var(--red_light); border:2px solid var(--red_dark); color:var(--red_dark); border-radius:10px; font-size:15px; font-weight:700; padding:8px 12px; text-align:center; }
.score-bar-wrap { margin-bottom:8px; }
.score-bar-label { display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px; }
.score-bar-track { height:8px; background:var(--gray_200); border-radius:4px; overflow:hidden; }
.score-bar-fill { height:100%; border-radius:4px; }
.improve-step { background:var(--white); border:1px solid var(--gray_200); border-radius:12px; padding:14px; margin-bottom:10px; }
.improve-num { font-size:10px; font-weight:700; color:var(--gray_500); margin-bottom:4px; }
.improve-desc { font-size:13px; color:var(--text_dark); line-height:1.6; }
.ai-loading-wrap { text-align:center; padding:48px 16px; }
.robot-icon { font-size:72px; margin-bottom:16px; animation:float 2s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
.ai-loading-title { font-family:'DM Serif Display',serif; font-size:26px; color:var(--green_dark); margin-bottom:16px; }
.ai-loading-sub { font-size:13px; color:var(--gray_500); }
.encouraging-box { background:linear-gradient(135deg,var(--green_light),#d4edda); border-left:4px solid var(--green_mid); border-radius:8px; padding:14px 16px; margin:14px 0; font-size:14px; color:var(--green_dark); font-style:italic; }
.factor-row { display:flex; justify-content:space-between; align-items:flex-start; font-size:12px; padding:8px 0; border-bottom:1px dashed var(--gray_100); gap:10px; }
.factor-label { color:var(--text_dark); font-weight:600; flex:0 0 auto; }
.factor-reason { color:var(--gray_500); flex:1; text-align:right; }
.factor-score { font-weight:700; flex:0 0 auto; min-width:40px; text-align:right; }
.upload-box { background:var(--green_light); border:2px dashed var(--green_dark); border-radius:10px; padding:12px 16px; margin-bottom:8px; }
.stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div, .stTextArea > div > div > textarea { border-radius:8px !important; border:1.5px solid var(--gray_200) !important; font-family:'DM Sans',sans-serif !important; font-size:13px !important; }
label { font-size:11px !important; font-weight:700 !important; letter-spacing:0.8px !important; color:var(--green_dark) !important; text-transform:uppercase !important; }
.stButton > button { background:var(--green_dark) !important; color:var(--white) !important; border:none !important; border-radius:8px !important; font-family:'DM Sans',sans-serif !important; font-weight:600 !important; font-size:14px !important; padding:10px 20px !important; width:100% !important; }
.stButton > button:hover { background:var(--green_mid) !important; }
.stProgress > div > div > div { background:var(--green_mid) !important; }
.stDownloadButton > button { background:var(--green_dark) !important; color:var(--white) !important; border:none !important; border-radius:8px !important; font-weight:600 !important; width:100% !important; }
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "page": "welcome", "lang": "EN", "agree": False,
        "form_data": {}, "ai_result": None,
        "report_id": "", "stakeholders_login": False,
        "stakeholder_report_id": "",
        "uploaded_images": [],  # list of {bytes, type, name}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def T(key):
    return lang[st.session_state.lang].get(key, key)

def gen_report_id():
    return "RPT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

def go(page):
    st.session_state["page"] = page
    st.rerun()


def generate_pdf(result, form_data, report_id):
    """Generate a proper PDF using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)

        GREEN_DARK = colors.HexColor("#0d4a24")
        GREEN_MID  = colors.HexColor("#1a7a3c")
        GREEN_LIGHT= colors.HexColor("#e8f5ed")
        RED        = colors.HexColor("#b91c1c")
        GRAY       = colors.HexColor("#888888")

        styles = getSampleStyleSheet()
        title_style  = ParagraphStyle("title",  fontName="Helvetica-Bold", fontSize=22, textColor=GREEN_DARK, spaceAfter=4)
        h2_style     = ParagraphStyle("h2",     fontName="Helvetica-Bold", fontSize=13, textColor=GREEN_DARK, spaceBefore=12, spaceAfter=4)
        body_style   = ParagraphStyle("body",   fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#1a1a1a"), spaceAfter=4, leading=14)
        small_style  = ParagraphStyle("small",  fontName="Helvetica",      fontSize=8,  textColor=GRAY)
        center_style = ParagraphStyle("center", fontName="Helvetica-Bold", fontSize=28, textColor=GREEN_MID, alignment=TA_CENTER)

        decision = result.get("decision", "—")
        score    = result.get("credit_score", 0)
        rec      = result.get("loan_recommendation", {})
        bd       = result.get("score_breakdown", {})
        tips     = result.get("improvement_tips", [])
        now      = datetime.now().strftime("%d %b %Y, %H:%M")

        story = []

        # Header
        story.append(Paragraph("💰 KreditX", title_style))
        story.append(Paragraph("AI-Powered Micro-Loan Assessment Report", ParagraphStyle("sub", fontName="Helvetica", fontSize=11, textColor=GREEN_MID, spaceAfter=2)))
        story.append(Paragraph(f"Report ID: {report_id}  |  Generated: {now}", small_style))
        story.append(HRFlowable(width="100%", thickness=2, color=GREEN_DARK, spaceAfter=12))

        # Decision banner
        d_color = GREEN_MID if decision == "QUALIFIED" else RED
        story.append(Paragraph(decision, ParagraphStyle("decision", fontName="Helvetica-Bold", fontSize=16, textColor=d_color, alignment=TA_CENTER, spaceBefore=6, spaceAfter=2)))
        story.append(Paragraph(str(score), center_style))
        story.append(Paragraph("CREDIT SCORE / 100", ParagraphStyle("scorelbl", fontName="Helvetica-Bold", fontSize=9, textColor=GREEN_MID, alignment=TA_CENTER, spaceAfter=8, letterSpacing=1)))

        # Summary
        if result.get("summary"):
            story.append(Paragraph("AI Summary", h2_style))
            story.append(Paragraph(result["summary"], body_style))

        if result.get("encouraging_message"):
            story.append(Paragraph(f'"{result["encouraging_message"]}"', ParagraphStyle("enc", fontName="Helvetica-Oblique", fontSize=10, textColor=GREEN_DARK, spaceAfter=8, leftIndent=10, borderPad=4)))

        # Applicant info
        story.append(Paragraph("Applicant Information", h2_style))
        info_data = [
            ["Business Name", form_data.get("biz_name","—")],
            ["Business Type", form_data.get("biz_type","—")],
            ["State",         form_data.get("state","—")],
            ["Years Operating", str(form_data.get("years","—"))],
            ["Daily Sales",   f"RM {float(form_data.get('daily_sales',0)):,.2f}"],
            ["Monthly Expenses", f"RM {float(form_data.get('monthly_exp',0)):,.2f}"],
            ["Loan Requested", f"RM {float(form_data.get('loan_amount',0)):,.2f}"],
        ]
        t = Table(info_data, colWidths=[60*mm, 110*mm])
        t.setStyle(TableStyle([
            ("FONTNAME",  (0,0),(-1,-1), "Helvetica"),
            ("FONTNAME",  (0,0),(0,-1),  "Helvetica-Bold"),
            ("FONTSIZE",  (0,0),(-1,-1), 9),
            ("TEXTCOLOR", (0,0),(0,-1),  GRAY),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, GREEN_LIGHT]),
            ("GRID",      (0,0),(-1,-1), 0.5, colors.HexColor("#e8e8e8")),
            ("PADDING",   (0,0),(-1,-1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))

        # Score breakdown
        if bd:
            story.append(Paragraph("Credit Score Breakdown", h2_style))
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
                ("FONTNAME",    (0,0),(-1,0),  "Helvetica-Bold"),
                ("FONTNAME",    (0,1),(-1,-1), "Helvetica"),
                ("FONTSIZE",    (0,0),(-1,-1), 9),
                ("BACKGROUND",  (0,0),(-1,0),  GREEN_DARK),
                ("TEXTCOLOR",   (0,0),(-1,0),  colors.white),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, GREEN_LIGHT]),
                ("GRID",        (0,0),(-1,-1), 0.5, colors.HexColor("#e8e8e8")),
                ("PADDING",     (0,0),(-1,-1), 5),
                ("ALIGN",       (1,0),(1,-1),  "CENTER"),
            ]))
            story.append(bt)
            story.append(Spacer(1, 8))

        # Loan recommendation
        if decision == "QUALIFIED" and rec:
            story.append(Paragraph("Loan Recommendation", h2_style))
            rec_data = []
            if rec.get("approved_amount_min") and rec.get("approved_amount_max"):
                rec_data.append(["Approved Amount", f"RM {rec['approved_amount_min']:,} — RM {rec['approved_amount_max']:,}"])
            if rec.get("recommended_scheme"):
                rec_data.append(["Recommended Scheme", rec["recommended_scheme"]])
            if rec.get("interest_rate_pct"):
                rec_data.append(["Interest Rate", f"{rec['interest_rate_pct']}% per year"])
            if rec.get("monthly_repayment_rm"):
                rec_data.append(["Monthly Repayment", f"RM {rec['monthly_repayment_rm']:,} / month"])
            if rec.get("repayment_months"):
                rec_data.append(["Repayment Period", f"{rec['repayment_months']} months"])
            if rec_data:
                rt = Table(rec_data, colWidths=[60*mm, 110*mm])
                rt.setStyle(TableStyle([
                    ("FONTNAME",  (0,0),(-1,-1), "Helvetica"),
                    ("FONTNAME",  (0,0),(0,-1),  "Helvetica-Bold"),
                    ("FONTSIZE",  (0,0),(-1,-1), 9),
                    ("TEXTCOLOR", (0,0),(0,-1),  GRAY),
                    ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, GREEN_LIGHT]),
                    ("GRID",      (0,0),(-1,-1), 0.5, colors.HexColor("#e8e8e8")),
                    ("PADDING",   (0,0),(-1,-1), 5),
                ]))
                story.append(rt)

        # Improvement tips
        valid_tips = [t for t in tips if t]
        if valid_tips:
            story.append(Paragraph("Steps to Improve", h2_style))
            for i, tip in enumerate(valid_tips, 1):
                story.append(Paragraph(f"{i}. {tip}", body_style))

        if result.get("come_back_in"):
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"📅 Recommended to reapply in: {result['come_back_in']}", ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#A46034"), spaceAfter=4)))

        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=GREEN_LIGHT, spaceBefore=12, spaceAfter=4))
        story.append(Paragraph("This report is generated by KreditX AI. It is for reference purposes only and does not constitute a formal credit approval.", small_style))

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        # Fallback: plain text if reportlab not installed
        lines = [
            "KREDITX AI LOAN ASSESSMENT REPORT",
            "="*50,
            f"Report ID: {report_id}",
            f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
            "",
            f"DECISION: {result.get('decision','—')}",
            f"CREDIT SCORE: {result.get('credit_score','—')}/100",
            "",
            f"BUSINESS: {form_data.get('biz_name','—')}",
            f"TYPE: {form_data.get('biz_type','—')}",
            f"STATE: {form_data.get('state','—')}",
            "",
            f"SUMMARY: {result.get('summary','')}",
            "",
            f"MESSAGE: {result.get('encouraging_message','')}",
        ]
        rec = result.get("loan_recommendation", {})
        if rec.get("recommended_scheme"):
            lines += ["", "LOAN RECOMMENDATION:", f"  Scheme: {rec.get('recommended_scheme')}", f"  Amount: RM{rec.get('approved_amount_min',0):,} - RM{rec.get('approved_amount_max',0):,}", f"  Rate: {rec.get('interest_rate_pct')}%", f"  Monthly: RM{rec.get('monthly_repayment_rm',0):,}"]
        tips = [t for t in result.get("improvement_tips",[]) if t]
        if tips:
            lines += ["", "IMPROVEMENT STEPS:"] + [f"  {i+1}. {t}" for i,t in enumerate(tips)]
        return "\n".join(lines).encode("utf-8")


def call_backend(form_data, uploaded_images=None):
    fd = form_data
    files = []

    # ✅ Multiple images as multipart
    if uploaded_images:
        for img in uploaded_images:
            files.append(("evidence_images", (img["name"], img["bytes"], img["type"])))

    data = {
        "biz_name":     fd.get("biz_name", ""),
        "biz_type":     fd.get("biz_type", ""),
        "biz_state":    fd.get("state", ""),
        "biz_year":     int(fd.get("years", 1)),
        "fin_sales":    float(fd.get("daily_sales", 0)),
        "fin_expenses": float(fd.get("monthly_exp", 0)),
        "fin_inventory":float(fd.get("inventory", 0)),
        "loan_amount":  float(fd.get("loan_amount", 0)),
        "reason":       fd.get("reason", ""),
        "voice_text":   fd.get("voice_text", ""),
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/evaluate-loan",
            data=data,
            files=files if files else None,
            timeout=140,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to backend at {BACKEND_URL}. Is the server running?"}
    except Exception as e:
        return {"error": str(e)}


def render_nav():
    current_lang = st.session_state.lang
    bm_style = "font-weight:800; color:#0d4a24;" if current_lang == "BM" else "color:#555;"
    en_style = "font-weight:800; color:#0d4a24;" if current_lang == "EN" else "color:#555;"
    login_label = "LOGOUT" if st.session_state.get("stakeholders_login") else T("stakeholders_login")
    st.markdown(f"""
    <div style="background:#e8f5ed; padding:16px 24px; display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:700; color:#0d4a24;">💰 KreditX</div>
        <div style="display:flex; align-items:center; gap:14px;">
            <a href="?lang=BM" target="_self" style="text-decoration:none; font-size:14px; font-weight:600; {bm_style}">BM</a>
            <span style="color:#aaa;">|</span>
            <a href="?lang=EN" target="_self" style="text-decoration:none; font-size:14px; font-weight:600; {en_style}">EN</a>
            <a href="?login=1" target="_self" style="text-decoration:none; border:2px solid #0d4a24; color:#0d4a24; font-size:12px; font-weight:700; padding:6px 14px; border-radius:4px;">{login_label}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    params = st.query_params
    if "lang" in params:
        st.session_state.lang = params["lang"]
    if "login" in params:
        if st.session_state.get("stakeholders_login"):
            st.session_state.stakeholders_login = False
        st.query_params.clear()
        go("welcome")

def render_footer():
    st.markdown(f"""
    <div style="background:#e8f5ed; padding:16px 24px; margin-top:40px; display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; gap:24px;">
            <a href="?page=form" target="_self" style="text-decoration:none; font-size:14px; color:#1a1a1a;">{T("user_form")}</a>
            <a href="?page=stakeholder_dashboard" target="_self" style="text-decoration:none; font-size:14px; color:#1a1a1a;">{T("stakeholder_dashboard")}</a>
        </div>
        <span style="color:#888; font-size:14px;">{T("copyright")}</span>
    </div>
    """, unsafe_allow_html=True)

def render_stepper(active=1):
    steps = [T("step1"), T("step2"), T("step3")]
    html = '<div class="stepper">'
    for i, label in enumerate(steps, 1):
        circle_class = "active" if i == active else ("done" if i < active else "")
        label_class = "active" if i == active else ""
        icon = "✓" if i < active else str(i)
        html += f'<div class="step-item"><div class="step-circle {circle_class}">{icon}</div><div class="step-label {label_class}">{label}</div></div>'
        if i < len(steps):
            line_class = "done" if i < active else ""
            html += f'<div class="step-line {line_class}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def page_welcome():
    render_nav()
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-badge">🤖 {T("ai_badge")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-title">{T("welcome_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-sub">{T("welcome_sub")}</div>', unsafe_allow_html=True)
    if st.button(T("start_btn"), key="start_btn"):
        go("form")
    agree = st.checkbox(T("agree"), value=st.session_state.agree)
    st.session_state.agree = agree
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:20px; font-weight:700; color:var(--green_mid); margin-bottom:14px;">{T("login_title")}</div>', unsafe_allow_html=True)
    email = st.text_input(T("email"), placeholder="email@example.com", key="login_email")
    password = st.text_input(T("password"), type="password", key="login_password")
    if st.button(T("login_btn"), key="login_btn"):
        if email and password:
            st.session_state.stakeholders_login = True
            go("stakeholder_dashboard")
        else:
            st.error("Please enter email and password.")
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def page_form():
    render_nav()
    render_stepper(1)
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # Voice box
    st.markdown(f"""
    <div style="background:#e8f5ed; border:2px dashed #0d4a24; border-radius:10px; padding:12px 16px; margin-bottom:16px;">
        <div style="font-size:15px; color:#1a1a1a; line-height:1.5; margin-bottom:8px;">{T('voice_sub')}</div>
    </div>
    """, unsafe_allow_html=True)
    audio = st.audio_input("", label_visibility="collapsed", key="voice_input")
    if audio:
        st.success("✅ Audio received!" if st.session_state.lang == "EN" else "✅ Audio diterima!")

    st.markdown(f'<div class="section-label">{T("biz_info")}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        biz_name = st.text_input(T("biz_name"), placeholder=T("biz_name_ph"), key="f_biz_name")
    with col2:
        biz_type = st.selectbox(T("biz_type"), [""] + T("biz_types"), key="f_biz_type")
    col3, col4 = st.columns(2)
    with col3:
        state = st.selectbox(T("biz_state"), [""] + T("biz_states"), key="f_biz_state")
    with col4:
        years = st.number_input(T("biz_year"), min_value=0, max_value=50, step=1, key="f_years")

    st.markdown(f'<div class="section-label">{T("fin_info")}</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        daily_sales = st.number_input(T("fin_sales"), min_value=0.0, step=10.0, format="%.2f", key="f_daily")
    with col6:
        monthly_exp = st.number_input(T("fin_expenses"), min_value=0.0, step=100.0, format="%.2f", key="f_monthly")
    inventory = st.number_input(T("fin_inventory"), min_value=0.0, step=100.0, format="%.2f", key="f_inventory")

    st.markdown(f'<div class="section-label">{T("voice_evidence")}</div>', unsafe_allow_html=True)
    voice_text = st.text_area("", placeholder=T("voice_evidence_ph"), height=100, key="f_voice_text", label_visibility="collapsed")

    #  Multiple image upload
    st.markdown(f'<div class="section-label">{T("upload_photo")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:12px; color:var(--gray_500); margin-bottom:8px;">{T("upload_photo_sub")}</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "", type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="f_photos",
        label_visibility="collapsed"
    )
    if uploaded_files:
        st.markdown(f'<div style="font-size:12px; color:var(--green_mid); margin-bottom:8px;">✅ {len(uploaded_files)} file(s) selected</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(uploaded_files), 4))
        imgs_data = []
        for i, f in enumerate(uploaded_files):
            raw = f.read()
            imgs_data.append({"bytes": raw, "type": f.type or "image/jpeg", "name": f.name})
            with cols[i % 4]:
                st.image(raw, caption=f.name[:15], width=120)
        st.session_state.uploaded_images = imgs_data
    else:
        st.session_state.uploaded_images = []

    loan_amount = st.number_input(T("loan_amount"), min_value=0.0, step=1000.0, format="%.2f", key="f_loan")
    reason = st.text_area(T("reason"), height=80, key="f_reason")

    if st.button(T("submit"), key="submit_form"):
        if not biz_name:
            st.error("Please enter business name.")
        elif daily_sales <= 0:
            st.error("Please enter daily sales.")
        elif loan_amount <= 0:
            st.error("Please enter loan amount.")
        else:
            st.session_state.form_data = {
                "biz_name": biz_name, "biz_type": biz_type, "state": state,
                "years": years, "daily_sales": daily_sales,
                "monthly_exp": monthly_exp, "inventory": inventory,
                "loan_amount": loan_amount, "reason": reason,
                "voice_text": voice_text,
                "photo_count": len(uploaded_files) if uploaded_files else 0,
            }
            go("summary")

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def page_summary():
    render_nav()
    render_stepper(2)
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    fd = st.session_state.form_data
    n_photos = fd.get("photo_count", 0)
    photo_text = f"✅ {n_photos} photo(s)" if n_photos > 0 else "—"
    rows = [
        (T("biz_name_lbl"), fd.get("biz_name","—")),
        (T("biz_type_lbl"), fd.get("biz_type","—")),
        (T("biz_state_lbl"), fd.get("state","—")),
        (T("fin_sales_lbl"), f"RM {fd.get('daily_sales',0):,.2f} / day"),
        (T("fin_expenses_lbl"), f"RM {fd.get('monthly_exp',0):,.2f} / month"),
        (T("fin_inventory_lbl"), f"RM {fd.get('inventory',0):,.2f}"),
        (T("documents"), photo_text),
        (T("loan_lbl"), f"RM {fd.get('loan_amount',0):,.2f}"),
    ]
    html = f'<div class="card"><div style="font-weight:700; font-size:15px; margin-bottom:12px; color:var(--green_dark);">{T("summary_title")}</div>'
    for k, v in rows:
        html += f'<div class="summary-row"><span class="summary-key">{k}</span><span class="summary-val">{v}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    if fd.get("voice_text"):
        st.markdown(f'<div style="font-size:12px; color:var(--gray_500); margin-bottom:8px;">💬 Chat evidence: {len(fd["voice_text"])} characters</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:17px; font-weight:600; color:var(--green_dark); margin-bottom:10px;">{T("info_confirm")}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(T("yes_btn"), key="yes_btn"):
            go("ai_loading")
    with col2:
        if st.button(T("no_btn"), key="no_btn"):
            go("form")
    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def page_ai_loading():
    render_nav()
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="ai-loading-wrap">
        <div class="robot-icon">🤖</div>
        <div class="ai-loading-title">{T('loading_title')}</div>
        <div class="ai-loading-sub">{T('loading_sub')}</div>
    </div>
    """, unsafe_allow_html=True)
    progress = st.progress(0)
    status = st.empty()
    steps = ["Collecting data...", "Analysing financials...", "Computing credit score...", "Generating report..."]
    if st.session_state.lang == "BM":
        steps = ["Mengumpul data...", "Menganalisis kewangan...", "Mengira skor kredit...", "Menjana laporan..."]

    for i in range(81):
        time.sleep(0.04)
        progress.progress(i)
        status.markdown(f'<div style="text-align:center; font-size:12px; color:var(--gray_500);">{steps[min(i//25, 3)]}</div>', unsafe_allow_html=True)

    result = call_backend(st.session_state.form_data, st.session_state.get("uploaded_images", []))

    for i in range(81, 101):
        time.sleep(0.02)
        progress.progress(i)

    if "error" in result:
        st.error(f"❌ {result['error']}")
        if result.get("details"):
            st.code(result["details"])
        if st.button("Try Again"):
            go("form")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.session_state.ai_result = result
    st.session_state.report_id = gen_report_id()
    st.markdown('</div>', unsafe_allow_html=True)
    go("result")


def page_result():
    render_nav()
    render_stepper(3)
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    result = st.session_state.get("ai_result")
    if not result:
        st.error("No result found.")
        if st.button("Start Over"):
            go("welcome")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if result.get("decision") == "QUALIFIED":
        _page_qualified(result)
    else:
        _page_not_qualified(result)

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def _render_score_breakdown(breakdown):
    if not breakdown:
        return
    labels = {
        "business_stability": ("🏪 Business Stability", 25),
        "financial_health":   ("💰 Financial Health",   25),
        "loan_purpose":       ("🎯 Loan Purpose",        20),
        "evidence_quality":   ("📋 Evidence Quality",   20),
        "repayment_capacity": ("📅 Repayment Capacity", 10),
    }
    html = f'<div class="card"><div class="section-label">{T("factors")}</div>'
    for key, (label, mx) in labels.items():
        item  = breakdown.get(key, {})
        s     = item.get("score", 0)
        reason= item.get("reason", "")
        color = "#16a34a" if s >= mx*0.7 else ("#f59e0b" if s >= mx*0.4 else "#ef4444")
        html += f'<div class="factor-row"><span class="factor-label">{label}</span><span class="factor-reason">{reason}</span><span class="factor-score" style="color:{color};">{s}/{mx}</span></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _page_qualified(result):
    score  = result.get("credit_score", 0)
    name   = st.session_state.form_data.get("biz_name", "")
    rec    = result.get("loan_recommendation", {})
    report_id = st.session_state.report_id

    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f'<div class="eligible-badge">{T("eligible")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:DM Serif Display,serif; font-size:22px; color:var(--green_dark); margin-top:8px;">{T("sub_title").format(name)}</div>', unsafe_allow_html=True)
    with col2:
        # ✅ Real PDF download
        pdf_bytes = generate_pdf(result, st.session_state.form_data, report_id)
        ext = "pdf" if pdf_bytes[:4] == b"%PDF" else "txt"
        st.download_button(T("download_PDF"), data=pdf_bytes, file_name=f"KreditX_report_{report_id}.{ext}", mime=f"application/{'pdf' if ext=='pdf' else 'text/plain'}", key="dl_pdf_q")

    if result.get("encouraging_message"):
        st.markdown(f'<div class="encouraging-box">💬 {result["encouraging_message"]}</div>', unsafe_allow_html=True)

    pct = score
    st.markdown(f"""
    <div class="card">
        <div class="section-label">{T('credit_score')}</div>
        <div class="score-ring-wrap">
            <div class="score-num">{score}</div>
            <div class="score-denom">/100</div>
            <div class="score-label">{T('good_score')}</div>
        </div>
        <div style="height:12px; background:var(--gray_200); border-radius:6px; overflow:hidden; margin:8px 0 14px;">
            <div style="height:100%; width:{pct}%; background:linear-gradient(90deg,#4ade80,#16a34a); border-radius:6px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if result.get("summary"):
        st.markdown(f'<div class="card"><div class="section-label">{T("summary_ai")}</div><div style="font-size:14px; line-height:1.7;">{result["summary"]}</div></div>', unsafe_allow_html=True)

    _render_score_breakdown(result.get("score_breakdown", {}))

    if rec:
        mn = rec.get("approved_amount_min"); mx2 = rec.get("approved_amount_max")
        if mn and mx2:
            st.markdown(f'<div class="loan-box"><div class="loan-box-label">{T("loan_range")}</div><div class="loan-box-val">RM {mn:,} — RM {mx2:,}</div></div>', unsafe_allow_html=True)
        if rec.get("interest_rate_pct"):
            st.markdown(f'<div class="loan-box"><div class="loan-box-label">{T("rate")}</div><div class="loan-box-val">{rec["interest_rate_pct"]}% <span style="font-size:14px; font-weight:400">/ year</span></div></div>', unsafe_allow_html=True)
        if rec.get("monthly_repayment_rm"):
            st.markdown(f'<div class="loan-box"><div class="loan-box-label">{T("monthly_pay")}</div><div class="loan-box-val">RM {rec["monthly_repayment_rm"]:,} <span style="font-size:14px; font-weight:400">/ month ({rec.get("repayment_months","36")} months)</span></div></div>', unsafe_allow_html=True)
        if rec.get("recommended_scheme"):
            st.markdown(f'<div class="loan-box"><div class="loan-box-label">{T("bank")}</div><div class="loan-box-val" style="font-size:18px;">{rec["recommended_scheme"]}</div></div>', unsafe_allow_html=True)


def _page_not_qualified(result):
    score  = result.get("credit_score", 0)
    name   = st.session_state.form_data.get("biz_name", "")
    tips   = result.get("improvement_tips", [])
    report_id = st.session_state.report_id

    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f'<div class="not-eligible-badge">{T("not_eligible")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:DM Serif Display,serif; font-size:20px; margin-top:8px;">{T("not_sub_title")}</div>', unsafe_allow_html=True)
    with col2:
        if st.button(T("again"), key="try_again"):
            go("form")

    if result.get("encouraging_message"):
        st.markdown(f'<div class="encouraging-box">💬 {result["encouraging_message"]}</div>', unsafe_allow_html=True)

    if result.get("summary"):
        st.markdown(f'<div class="card"><div class="section-label">{T("summary_ai")}</div><div style="font-size:14px; line-height:1.7;">{result["summary"]}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-label">{T("current_score")}</div>', unsafe_allow_html=True)
    bars = [(T("user_score"), score, 100, "#e57373"), (T("required_score"), 55, 100, "#ff9800"), (T("max_score"), 100, 100, "#4caf50")]
    bar_html = '<div class="card">'
    for label, val, mx, color in bars:
        pct = int(val/mx*100)
        bar_html += f'<div class="score-bar-wrap"><div class="score-bar-label"><span>{label}</span><span style="font-weight:700; color:{color}">{val}</span></div><div class="score-bar-track"><div class="score-bar-fill" style="width:{pct}%; background:{color};"></div></div></div>'
    bar_html += f'<div style="font-size:11px; color:#ff9800; margin-top:8px;">{T("retry_note")}</div></div>'
    st.markdown(bar_html, unsafe_allow_html=True)

    if result.get("come_back_in"):
        st.markdown(f'<div style="background:var(--yellow_light); border:1px solid #fbbf24; border-radius:8px; padding:10px 14px; font-size:13px; color:var(--yellow_dark); margin-bottom:14px;">📅 {T("come_back")}: <strong>{result["come_back_in"]}</strong></div>', unsafe_allow_html=True)

    valid_tips = [t for t in tips if t]
    if valid_tips:
        st.markdown(f'<div class="section-label">{T("step_improve")}</div>', unsafe_allow_html=True)
        for i, tip in enumerate(valid_tips, 1):
            st.markdown(f'<div class="improve-step"><div class="improve-num">0{i}</div><div class="improve-desc">{tip}</div></div>', unsafe_allow_html=True)

    _render_score_breakdown(result.get("score_breakdown", {}))

    #  Real PDF download
    pdf_bytes = generate_pdf(result, st.session_state.form_data, report_id)
    ext = "pdf" if pdf_bytes[:4] == b"%PDF" else "txt"
    st.download_button(T("download_PDF_btn"), data=pdf_bytes, file_name=f"kreditX_guide_{report_id}.{ext}", mime=f"application/{'pdf' if ext=='pdf' else 'text/plain'}", key="dl_pdf_nq")


def page_stakeholder_dashboard():
    render_nav()
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-family:DM Serif Display,serif; font-size:36px; color:var(--green_dark);">{T("dashboard_title")}</div>',
        unsafe_allow_html=True)

    # ── Stats from DB ─────────────────────────────────────────────────────────
    try:
        stats_resp = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f'<div style="background:var(--green_light); border-radius:10px; padding:12px; text-align:center;"><div style="font-size:10px; color:var(--gray_500);">TOTAL REPORTS</div><div style="font-size:24px; font-weight:800; color:var(--green_dark);">{stats.get("total", 0)}</div></div>',
                    unsafe_allow_html=True)
            with col2:
                st.markdown(
                    f'<div style="background:#e8f5ed; border-radius:10px; padding:12px; text-align:center;"><div style="font-size:10px; color:var(--gray_500);">QUALIFIED</div><div style="font-size:24px; font-weight:800; color:#16a34a;">{stats.get("qualified", 0)}</div></div>',
                    unsafe_allow_html=True)
            with col3:
                st.markdown(
                    f'<div style="background:#fbe9e9; border-radius:10px; padding:12px; text-align:center;"><div style="font-size:10px; color:var(--gray_500);">NOT QUALIFIED</div><div style="font-size:24px; font-weight:800; color:#b91c1c;">{stats.get("not_qualified", 0)}</div></div>',
                    unsafe_allow_html=True)
            with col4:
                avg = stats.get("avg_score")
                avg_str = f"{avg:.1f}" if avg else "—"
                st.markdown(
                    f'<div style="background:var(--green_light); border-radius:10px; padding:12px; text-align:center;"><div style="font-size:10px; color:var(--gray_500);">AVG SCORE</div><div style="font-size:24px; font-weight:800; color:var(--green_dark);">{avg_str}</div></div>',
                    unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    except:
        pass

    # ── Search by report ID ───────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:13px; color:var(--gray_500); margin-bottom:10px;">{T("enter")}</div>',
                unsafe_allow_html=True)
    report_id_input = st.text_input("", placeholder="RPT-XXXXXXXX", label_visibility="collapsed",
                                    key="stakeholder_id_input")

    if st.button(T("view_report"), key="view_report_btn"):
        if report_id_input.strip():
            # ── Fetch from DB via backend ─────────────────────────────────────
            try:
                resp = requests.get(f"{BACKEND_URL}/report/{report_id_input.strip()}", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.stakeholder_report_id = report_id_input.strip()
                    st.session_state.stakeholder_db_data = data
                    go("stakeholder_report")
                elif resp.status_code == 404:
                    st.error(f"Report '{report_id_input}' not found in database.")
                else:
                    st.error("Error fetching report. Is the backend running?")
            except Exception as e:
                st.error(f"Cannot connect to backend: {e}")
        else:
            st.error("Please enter a Report ID.")

    # ── Recent reports list ───────────────────────────────────────────────────
    try:
        list_resp = requests.get(f"{BACKEND_URL}/reports?limit=10", timeout=5)
        if list_resp.status_code == 200:
            reports = list_resp.json()
            if reports:
                st.markdown('<div class="section-label" style="margin-top:20px;">RECENT REPORTS</div>',
                            unsafe_allow_html=True)
                html = '<div class="card">'
                for r in reports:
                    d_color = "#16a34a" if r.get("decision") == "QUALIFIED" else "#b91c1c"
                    html += f'''<div class="summary-row">
                        <span class="summary-key" style="flex:2;">{r.get("biz_name", "—")}</span>
                        <span style="flex:1; font-size:11px; color:var(--gray_500);">{r.get("report_id", "")}</span>
                        <span style="flex:1; font-size:11px; color:var(--gray_500);">{r.get("created_at", "")[:10]}</span>
                        <span style="flex:0 0 auto; font-weight:700; color:{d_color}; font-size:12px;">{r.get("decision", "—")}</span>
                    </div>'''
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
    except:
        pass

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def page_stakeholder_report():
    render_nav()
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    report_id = st.session_state.get("stakeholder_report_id", "")
    db_data = st.session_state.get("stakeholder_db_data", {})

    # Use DB data if available, else fall back to session
    if db_data:
        result = db_data.get("result", {})
        fd = db_data.get("form_data", {})
        created = db_data.get("created_at", "")
    else:
        result = st.session_state.get("ai_result", {})
        fd = st.session_state.form_data or {}
        created = ""

    biz_name = fd.get("biz_name", "—")
    biz_type = fd.get("biz_type", "—")
    state = fd.get("state", "—")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f'<div style="font-family:DM Serif Display,serif; font-size:26px; color:var(--green_dark);">{biz_name}</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:12px; color:var(--gray_500);">{biz_type} • {state} • Report ID: <strong>{report_id}</strong></div>',
            unsafe_allow_html=True)
        if created:
            st.markdown(f'<div style="font-size:11px; color:var(--gray_500);">Submitted: {created}</div>',
                        unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div style="background:var(--green_light); border-radius:8px; padding:6px 10px; font-size:11px; font-weight:700; color:var(--green_mid); text-align:center;">{T("applicant")}</div>',
            unsafe_allow_html=True)

    if result:
        decision = result.get("decision", "—")
        score = result.get("credit_score", 0)
        d_color = "#16a34a" if decision == "QUALIFIED" else "#b91c1c"
        d_bg = "#e8f5ed" if decision == "QUALIFIED" else "#fbe9e9"

        col3, col4, col5 = st.columns(3)
        with col3:
            st.markdown(
                f'<div style="background:{d_bg}; border-radius:10px; padding:12px; text-align:center; margin-bottom:10px;"><div style="font-size:10px; color:var(--gray_500);">AI DECISION</div><div style="font-size:14px; font-weight:700; color:{d_color};">{decision}</div><div style="font-size:28px; font-weight:800; color:{d_color};">{score}/100</div></div>',
                unsafe_allow_html=True)
        with col4:
            monthly_income = float(fd.get("daily_sales", 0)) * 30
            st.markdown(
                f'<div style="background:var(--white); border:1px solid var(--gray_200); border-radius:10px; padding:12px; margin-bottom:10px;"><div style="font-size:10px; color:var(--gray_500);">💰 EST. MONTHLY INCOME</div><div style="font-size:16px; font-weight:700; color:var(--green_dark);">RM {monthly_income:,.0f}</div></div>',
                unsafe_allow_html=True)
        with col5:
            loan_amt = float(fd.get("loan_amount", 0))
            st.markdown(
                f'<div style="background:var(--white); border:1px solid var(--gray_200); border-radius:10px; padding:12px; margin-bottom:10px;"><div style="font-size:10px; color:var(--gray_500);">🏦 LOAN REQUESTED</div><div style="font-size:16px; font-weight:700; color:var(--green_dark);">RM {loan_amt:,.0f}</div></div>',
                unsafe_allow_html=True)

        if result.get("summary"):
            st.markdown(
                f'<div class="card"><div class="section-label">AI SUMMARY</div><div style="font-size:13px; line-height:1.7;">{result["summary"]}</div></div>',
                unsafe_allow_html=True)

        if result.get("encouraging_message"):
            st.markdown(f'<div class="encouraging-box">💬 {result["encouraging_message"]}</div>', unsafe_allow_html=True)

        _render_score_breakdown(result.get("score_breakdown", {}))

        rec = result.get("loan_recommendation", {})
        if decision == "QUALIFIED" and rec:
            st.markdown('<div class="section-label">LOAN RECOMMENDATION</div>', unsafe_allow_html=True)
            if rec.get("approved_amount_min") and rec.get("approved_amount_max"):
                st.markdown(
                    f'<div class="loan-box"><div class="loan-box-label">APPROVED AMOUNT</div><div class="loan-box-val">RM {rec["approved_amount_min"]:,} — RM {rec["approved_amount_max"]:,}</div></div>',
                    unsafe_allow_html=True)
            if rec.get("recommended_scheme"):
                st.markdown(
                    f'<div class="loan-box"><div class="loan-box-label">RECOMMENDED SCHEME</div><div class="loan-box-val" style="font-size:18px;">{rec["recommended_scheme"]}</div></div>',
                    unsafe_allow_html=True)

        tips = [t for t in result.get("improvement_tips", []) if t]
        if tips:
            st.markdown('<div class="section-label">IMPROVEMENT STEPS</div>', unsafe_allow_html=True)
            for i, tip in enumerate(tips, 1):
                st.markdown(
                    f'<div class="improve-step"><div class="improve-num">0{i}</div><div class="improve-desc">{tip}</div></div>',
                    unsafe_allow_html=True)

    else:
        st.info("No AI result found for this report.")

    now = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f'<div style="font-size:11px; color:var(--gray_500); margin:10px 0;">{T("gen_report")} {now}</div>',
                unsafe_allow_html=True)

    col_b, col_d = st.columns(2)
    with col_b:
        if st.button(T("back_btn"), key="back_stakeholder"):
            st.session_state.stakeholder_db_data = {}
            go("stakeholder_dashboard")
    with col_d:
        # ✅ Download PDF directly from DB
        if report_id:
            try:
                pdf_resp = requests.get(f"{BACKEND_URL}/report/{report_id}/pdf", timeout=10)
                if pdf_resp.status_code == 200:
                    st.download_button(
                        T("download_btn"),
                        data=pdf_resp.content,
                        file_name=f"kreditx_{report_id}.pdf",
                        mime="application/pdf",
                        key="dl_pdf_stakeholder"
                    )
            except:
                st.warning("PDF download unavailable.")

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()




page = st.session_state["page"]
if   page == "welcome":               page_welcome()
elif page == "form":                  page_form()
elif page == "summary":               page_summary()
elif page == "ai_loading":            page_ai_loading()
elif page == "result":                page_result()
elif page == "stakeholder_dashboard": page_stakeholder_dashboard()
elif page == "stakeholder_report":    page_stakeholder_report()
else:                                 page_welcome()

#updated_last