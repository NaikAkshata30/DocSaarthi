from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether
)

OUT = Path(__file__).resolve().parents[1] / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#16324F")
SAFFRON = colors.HexColor("#D97706")
GREEN = colors.HexColor("#1F6F54")
PALE = colors.HexColor("#F3F6F8")
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#52616B")
BORDER = colors.HexColor("#C9D2D9")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="GovTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, alignment=TA_CENTER, spaceAfter=5))
styles.add(ParagraphStyle(name="GovSub", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY, spaceBefore=11, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyLegal", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=14, textColor=INK, alignment=TA_LEFT, spaceAfter=7))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.4, leading=10, textColor=MUTED))
styles.add(ParagraphStyle(name="Label", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=MUTED))
styles.add(ParagraphStyle(name="Value", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9.2, leading=12, textColor=INK))
styles.add(ParagraphStyle(name="Notice", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.HexColor("#8B1E1E"), alignment=TA_CENTER))

def header_footer(canvas, doc, code):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 21*mm, w, 21*mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(18*mm, h - 10.5*mm, "NATIONAL PUBLIC SERVICES - DEMONSTRATION RECORD")
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(w - 18*mm, h - 10.5*mm, code)
    canvas.setStrokeColor(SAFFRON)
    canvas.setLineWidth(2)
    canvas.line(18*mm, h - 22.5*mm, w - 18*mm, h - 22.5*mm)
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1)
    canvas.line(18*mm, 18*mm, w - 18*mm, 18*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(18*mm, 12*mm, "FICTIONAL SAMPLE - FOR SOFTWARE TESTING AND TRAINING ONLY")
    canvas.drawRightString(w - 18*mm, 12*mm, f"Page {doc.page}")
    canvas.restoreState()

def field_grid(items):
    cells = []
    for label, value in items:
        cells.append([Paragraph(label.upper(), styles["Label"]), Paragraph(value, styles["Value"])])
    table = Table(cells, colWidths=[47*mm, 123*mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), PALE), ("BOX", (0,0), (-1,-1), .5, BORDER),
        ("INNERGRID", (0,0), (-1,-1), .35, BORDER), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return table

def clause(number, title, text):
    return KeepTogether([
        Paragraph(f"{number}. {title}", styles["Section"]),
        Paragraph(text, styles["BodyLegal"]),
    ])

def build_financial():
    path = OUT / "Official_Style_Sample_Financial_Loan_Sanction.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=30*mm, bottomMargin=24*mm, title="Fictional Financial Loan Sanction", author="DocSaarthi Test Materials")
    story = [
        Spacer(1, 5*mm), Paragraph("LOAN SANCTION AND REPAYMENT ORDER", styles["GovTitle"]),
        Paragraph("Office of Citizen Financial Facilitation (Fictional Demonstration Authority)", styles["GovSub"]),
        Paragraph("THIS IS NOT A REAL GOVERNMENT ORDER OR LOAN OFFER", styles["Notice"]), Spacer(1, 5*mm),
        field_grid([
            ("Order number", "OCFF/LOAN/2026/0417"), ("Issue date", "10 October 2026"),
            ("Applicant", "Arjun Mehta"), ("Lending institution", "Jan Seva Finance Corporation (Fictional)"),
            ("Principal amount", "INR 5,00,000"), ("Purpose", "Personal household expenditure"),
        ]),
        clause(1, "Sanction", "Subject to the conditions in this order, the Lending Institution sanctions a principal loan amount of INR 5,00,000 to the Applicant. The net proceeds shall be credited to the bank account registered in the Applicant's name after completion of identity and account verification."),
        clause(2, "Interest and Charges", "Interest shall be charged at a fixed annual rate of 9.50% on the reducing principal balance. Interest shall be calculated daily and applied monthly. A processing fee of INR 5,000 plus applicable taxes shall be deducted before disbursement."),
        clause(3, "Repayment Obligation", "The Borrower shall pay 36 monthly instalments of INR 16,026 each. Every instalment is due on or before the 5th day of each month through the repayment method registered with the Lender. The first instalment is due on 5 November 2026 and the final scheduled instalment is due on 5 October 2029. The final amount may vary slightly because of rounding or permitted adjustments."),
        clause(4, "Late Payment", "If an instalment remains unpaid for more than 5 calendar days after its due date, a late-payment charge of INR 500 may be applied, subject to applicable law. Late charges do not replace the obligation to pay the overdue instalment and accrued interest."),
        PageBreak(),
        Paragraph("TERMS, SAFEGUARDS AND DISCLOSURES", styles["GovTitle"]),
        Paragraph("Continuation of Order OCFF/LOAN/2026/0417", styles["GovSub"]),
        clause(5, "Prepayment", "The Borrower may request partial or full prepayment after 6 completed instalments. A prepayment fee of 2% of the principal amount prepaid, plus applicable taxes, may apply where permitted by law."),
        clause(6, "Events of Default", "An event of default occurs if the Borrower does not pay 2 consecutive instalments, provides materially false information, or uses the funds for an unlawful purpose. After default, the Lender may demand the outstanding balance, accrued interest, and lawful charges after giving any notice required by applicable law."),
        clause(7, "Statements and Receipts", "The Borrower may request an account statement, amortisation schedule, or payment receipt without charge. Any disputed transaction should be reported within 30 days of the statement date. Reporting a dispute does not suspend undisputed payment obligations."),
        clause(8, "Privacy and Credit Reporting", "The Lender may report accurate repayment information to authorised credit information companies. Personal data may be processed for servicing, fraud prevention, regulatory compliance, and recovery as permitted by law."),
        clause(9, "Grievance Redressal", "A written complaint may be submitted to the Grievance Officer at grievance@example.invalid. If unresolved within 30 days, the Borrower may use any regulator, ombudsman, court, or other remedy available under applicable law."),
        clause(10, "Governing Law", "This fictional testing document shall be governed by the laws applicable in the State of Maharashtra, India. Courts at Mumbai, Maharashtra have jurisdiction where legally permitted."),
        Spacer(1, 8*mm), field_grid([("Authorised signatory", "Neha Rao, Sample Accounts Officer"), ("Digital record reference", "DS-FIN-2026-500K-TEST"), ("Document status", "Fictional - Not legally enforceable")]),
    ]
    doc.build(story, onFirstPage=lambda c,d: header_footer(c,d,"FINANCIAL / SAMPLE"), onLaterPages=lambda c,d: header_footer(c,d,"FINANCIAL / SAMPLE"))
    return path

def build_legal():
    path = OUT / "Official_Style_Sample_Public_Service_Agreement.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=30*mm, bottomMargin=24*mm, title="Fictional Public Service Agreement", author="DocSaarthi Test Materials")
    story = [
        Spacer(1, 5*mm), Paragraph("PUBLIC SERVICE FACILITY AGREEMENT", styles["GovTitle"]),
        Paragraph("Department of Community Service Administration (Fictional Demonstration Authority)", styles["GovSub"]),
        Paragraph("THIS IS NOT A REAL GOVERNMENT AGREEMENT OR AUTHORIZATION", styles["Notice"]), Spacer(1, 5*mm),
        field_grid([
            ("Agreement number", "DCSA/PSF/2026/1182"), ("Effective date", "1 December 2026"),
            ("Authority", "Department of Community Service Administration (Fictional)"),
            ("Service provider", "Civic Support Solutions Private Limited"),
            ("Initial term", "24 months"), ("Service location", "Mumbai, Maharashtra"),
        ]),
        clause(1, "Purpose", "This Agreement appoints the Service Provider to operate a fictional citizen-document help desk, maintain service records, and provide scheduled support at the designated facility. No power of government, licensing authority, or law enforcement is delegated under this Agreement."),
        clause(2, "Term", "The Agreement begins on 1 December 2026 and continues for 24 months unless terminated earlier in accordance with Clause 9. Any extension must be recorded in a written amendment signed by both parties."),
        clause(3, "Service Standards", "The Service Provider shall maintain the facility from 9:00 a.m. to 5:00 p.m. on working days, acknowledge complaints within 2 working days, and preserve an auditable register of requests and actions."),
        clause(4, "Fees and Taxes", "The Authority shall pay a monthly service fee of INR 1,25,000 after verification of the monthly performance report. Applicable taxes shall be paid or deducted in accordance with law. No additional charge may be imposed without prior written approval."),
        clause(5, "Confidentiality", "Each party shall keep confidential information secure and use it only for this Agreement. Personal information shall be accessed only by authorised personnel and retained only for the period required by law or the approved records schedule."),
        PageBreak(),
        Paragraph("GENERAL CONDITIONS OF AGREEMENT", styles["GovTitle"]),
        Paragraph("Continuation of Agreement DCSA/PSF/2026/1182", styles["GovSub"]),
        clause(6, "Information Security", "The Service Provider shall apply reasonable administrative, technical, and physical safeguards. A suspected data incident must be reported to the Authority within 24 hours of discovery, together with available details and mitigation steps."),
        clause(7, "Audit and Records", "The Authority may inspect records reasonably related to the services after giving 5 working days written notice. Records shall be complete, accurate, and available for audit for 3 years after expiry or termination."),
        clause(8, "Breach and Corrective Action", "A party must cure a material breach within fifteen days after written notice. Where the breach creates an immediate risk to public safety, personal data, or public funds, the Authority may suspend the affected service pending corrective action."),
        clause(9, "Termination", "Either party may terminate this Agreement by giving thirty days prior written notice. The Authority may terminate immediately for fraud, unlawful conduct, deliberate disclosure of confidential information, or repeated material failure to meet service standards."),
        clause(10, "Dispute Resolution", "The parties shall first attempt to resolve the dispute through good-faith discussions. If the dispute remains unresolved for 30 days, either party may pursue mediation, arbitration, or any remedy available under applicable law."),
        clause(11, "Governing Law and Jurisdiction", "This Agreement is governed by the laws of India. Courts at Mumbai, Maharashtra have jurisdiction where legally permitted."),
        clause(12, "Notices", "All notices must be provided in writing to the registered address of the receiving party. Electronic notice is valid only when receipt is acknowledged by the designated officer."),
        Spacer(1, 7*mm), field_grid([("For the Authority", "Kavita Deshmukh, Sample Joint Director"), ("For the Service Provider", "Rahul Sen, Sample Authorised Representative"), ("Document status", "Fictional - Not legally enforceable")]),
    ]
    doc.build(story, onFirstPage=lambda c,d: header_footer(c,d,"LEGAL / SAMPLE"), onLaterPages=lambda c,d: header_footer(c,d,"LEGAL / SAMPLE"))
    return path

if __name__ == "__main__":
    print(build_financial())
    print(build_legal())
