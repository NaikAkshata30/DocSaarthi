from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUT = Path(__file__).resolve().parents[1] / "output" / "pdf" / "test-pack"
OUT.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont("Nirmala", r"C:\Windows\Fonts\Nirmala.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("Nirmala-Bold", r"C:\Windows\Fonts\Nirmala.ttc", subfontIndex=1))

NAVY = colors.HexColor("#173B57")
TEAL = colors.HexColor("#0D7C66")
PALE = colors.HexColor("#EEF4F6")
INK = colors.HexColor("#1A2630")
MUTED = colors.HexColor("#66737F")
RED = colors.HexColor("#A52B2B")

def styles_for(lang):
    base = getSampleStyleSheet()
    font = "Nirmala" if lang == "hi" else "Helvetica"
    bold = "Nirmala-Bold" if lang == "hi" else "Helvetica-Bold"
    return {
        "title": ParagraphStyle("title", fontName=bold, fontSize=14, leading=18, alignment=TA_CENTER, textColor=NAVY, spaceAfter=3),
        "sub": ParagraphStyle("sub", fontName=font, fontSize=7.8, leading=9, alignment=TA_CENTER, textColor=MUTED, spaceAfter=6),
        "h": ParagraphStyle("h", fontName=bold, fontSize=9.2, leading=11, textColor=NAVY, spaceBefore=5, spaceAfter=2),
        "body": ParagraphStyle("body", fontName=font, fontSize=8, leading=11, textColor=INK, spaceAfter=3),
        "small": ParagraphStyle("small", fontName=font, fontSize=7.5, leading=10, textColor=MUTED),
        "cell": ParagraphStyle("cell", fontName=font, fontSize=7.4, leading=9, textColor=INK),
        "cellb": ParagraphStyle("cellb", fontName=bold, fontSize=7.4, leading=9, textColor=INK),
        "warn": ParagraphStyle("warn", fontName=bold, fontSize=7.2, leading=9, alignment=TA_CENTER, textColor=RED, spaceAfter=5),
    }

def decorate(canvas, doc, lang, code, category):
    canvas.saveState(); w, h = A4
    canvas.setFillColor(NAVY); canvas.rect(0, h-18*mm, w, 18*mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(16*mm, h-10.5*mm, "DOCSAARTHI TEST DOCUMENT PACK")
    canvas.setFont("Helvetica", 7); canvas.drawRightString(w-16*mm, h-10.5*mm, f"{category} | {code}")
    canvas.setStrokeColor(TEAL); canvas.line(16*mm, 17*mm, w-16*mm, 17*mm)
    canvas.setFillColor(RED); canvas.setFont("Helvetica-Bold", 6.7)
    canvas.drawString(16*mm, 11*mm, "FICTIONAL SAMPLE - NOT VALID FOR ANY LEGAL, FINANCIAL OR GOVERNMENT PURPOSE")
    canvas.setFillColor(MUTED); canvas.drawRightString(w-16*mm, 11*mm, f"Page {doc.page}")
    canvas.saveState(); canvas.translate(w/2, h/2); canvas.rotate(40)
    canvas.setFillColor(colors.Color(.35,.42,.3,alpha=.07)); canvas.setFont("Helvetica-Bold", 42)
    canvas.drawCentredString(0, 0, "SAMPLE - NOT VALID"); canvas.restoreState(); canvas.restoreState()

def info_table(rows, s, widths=(48*mm, 122*mm)):
    data = [[Paragraph(str(a), s["cellb"]), Paragraph(str(b), s["cell"])] for a,b in rows]
    t = Table(data, colWidths=list(widths), hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),PALE),("GRID",(0,0),(-1,-1),.45,colors.HexColor("#9AA8B2")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t

def data_table(header, rows, s, widths):
    data = [[Paragraph(str(x), s["cellb"]) for x in header]] + [[Paragraph(str(x), s["cell"]) for x in row] for row in rows]
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),PALE),("TEXTCOLOR",(0,0),(-1,0),TEAL),("GRID",(0,0),(-1,-1),.45,colors.HexColor("#8E9CA6")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t

def create(filename, lang, category, code, title, subtitle, metadata, sections, tables=()):
    s = styles_for(lang); path = OUT / filename
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=23*mm, bottomMargin=19*mm, title=title, author="DocSaarthi Test Pack")
    if lang == "hi":
        letter_rows = [("दिनांक", "4 अक्टूबर 2026"), ("प्रति", "संबंधित दस्तावेज़ धारक"), ("संदर्भ", code), ("विषय", title)]
        salutation = "महोदय/महोदया,"
        intro = f"यह पत्र {subtitle} के संबंध में जारी किया गया एक काल्पनिक नमूना है। नीचे दिए गए विवरण, शर्तें, राशियाँ, तिथियाँ और दायित्व DocSaarthi में दस्तावेज़ वर्गीकरण, सूचना निष्कर्षण, जोखिम पहचान, अनुवाद, उद्धरण और प्रश्न-उत्तर परीक्षण के लिए उपलब्ध कराए गए हैं।"
        particulars = "दस्तावेज़ विवरण"
        closing = "भवदीय,<br/><b>नमूना दस्तावेज़ अधिकारी</b><br/>DocSaarthi परीक्षण अभिलेख कार्यालय"
    else:
        letter_rows = [("Date", "4 October 2026"), ("To", "The concerned document holder"), ("Reference", code), ("Subject", title)]
        salutation = "Dear Sir/Madam,"
        intro = f"This formal letter is a fictional sample concerning {subtitle.lower()}. The particulars, dates, amounts, obligations, risks and clauses below are provided for testing DocSaarthi document classification, information extraction, translation, citations and document-grounded question answering."
        particulars = "Document particulars"
        closing = "Yours faithfully,<br/><b>Sample Document Officer</b><br/>DocSaarthi Test Records Office"
    story = [Paragraph("FORMAL DOCUMENT LETTER" if lang=="en" else "औपचारिक दस्तावेज़ पत्र", s["title"]), Paragraph("DocSaarthi Test Records Office | Private software-testing correspondence", s["sub"]), Paragraph("काल्पनिक नमूना दस्तावेज़ - केवल सॉफ्टवेयर परीक्षण के लिए" if lang=="hi" else "FICTIONAL SAMPLE DOCUMENT - FOR SOFTWARE TESTING ONLY", s["warn"]), info_table(letter_rows, s), Spacer(1,3*mm), Paragraph(salutation, s["body"]), Paragraph(intro, s["body"]), Paragraph(f"<b>{particulars}</b>", s["h"]), info_table(metadata, s), Spacer(1,3*mm)]
    table_map = {at:(header,rows,widths) for at,header,rows,widths in tables}
    for i,(heading,body) in enumerate(sections,1):
        story += [Paragraph(f"{i}. {heading}", s["h"]), Paragraph(body, s["body"])]
        if i in table_map:
            header,rows,widths=table_map[i]; story += [data_table(header,rows,s,widths),Spacer(1,2*mm)]
    story += [Spacer(1,4*mm), Paragraph(closing, s["body"]), Spacer(1,3*mm), Paragraph(("घोषणा: इस दस्तावेज़ में सभी नाम, पते, राशियाँ और पहचान संख्या काल्पनिक हैं।" if lang=="hi" else "Declaration: All names, addresses, amounts and identifiers in this document are fictional."), s["small"])]
    doc.build(story, onFirstPage=lambda c,d:decorate(c,d,lang,code,category), onLaterPages=lambda c,d:decorate(c,d,lang,code,category))
    return path

docs = [
    dict(filename="Financial_EN_01_Personal_Loan_Agreement.pdf",lang="en",category="FINANCIAL",code="FIN-EN-01",title="PERSONAL LOAN AGREEMENT",subtitle="Loan account, repayment schedule and borrower obligations",metadata=[("Agreement ID","DS-PL-2026-041"),("Lender","Sunrise Community Finance Limited"),("Borrower","Arjun Mehta"),("Agreement date","10 October 2026"),("Principal","INR 5,00,000"),("Tenure","36 months")],sections=[("Loan and disbursement","The Lender agrees to lend and the Borrower agrees to borrow INR 5,00,000. A processing fee of INR 5,000 plus applicable taxes will be deducted before disbursement on 15 October 2026."),("Interest","Interest is charged at a fixed annual rate of 9.50% on the reducing principal balance and is calculated daily."),("Repayment","The Borrower shall pay 36 monthly instalments of INR 16,026 each. Every instalment is due on or before the 5th day of each month. The first instalment is due on 5 November 2026 and the final scheduled instalment is due on 5 October 2029."),("Late payment and default","A late-payment charge of INR 500 may apply when an instalment remains unpaid for more than 5 calendar days. Missing 2 consecutive instalments constitutes an event of default."),("Prepayment","The Borrower may request full or partial prepayment after 6 completed instalments. A fee of 2% of the prepaid principal plus tax may apply."),("Governing law","This Agreement is governed by the laws of India. Courts at Mumbai, Maharashtra have jurisdiction where legally permitted.")]),
    dict(filename="Financial_EN_02_Bank_Account_Statement.pdf",lang="en",category="FINANCIAL",code="FIN-EN-02",title="SAVINGS ACCOUNT STATEMENT",subtitle="Monthly transaction statement for September 2026",metadata=[("Account holder","Meera Joshi"),("Account number","XXXX XXXX 4821"),("Branch","Pune Central"),("Statement period","1 September 2026 to 30 September 2026"),("Opening balance","INR 84,250.00"),("Closing balance","INR 96,740.00")],sections=[("Transaction summary","The following entries represent deposits, withdrawals, charges and interest posted during the statement period."),("Important information","Report an unauthorised transaction within 30 days of the statement date. Interest credited is subject to applicable tax rules."),("Balance certification","The closing available balance on 30 September 2026 is INR 96,740.00. A minimum average balance of INR 10,000 is required.")],tables=[(1,["Date","Description","Debit (INR)","Credit (INR)","Balance (INR)"],[["03 Sep","Salary credit","-","75,000","1,59,250"],["05 Sep","House rent","28,000","-","1,31,250"],["12 Sep","Electricity bill","3,240","-","1,28,010"],["18 Sep","ATM withdrawal","10,000","-","1,18,010"],["27 Sep","Insurance premium","22,000","-","96,010"],["30 Sep","Interest credit","-","730","96,740"]],[24*mm,55*mm,29*mm,29*mm,33*mm])]),
    dict(filename="Financial_HI_01_Rin_Swikriti_Patra.pdf",lang="hi",category="FINANCIAL",code="FIN-HI-01",title="ऋण स्वीकृति एवं पुनर्भुगतान पत्र",subtitle="ऋण राशि, ब्याज दर, किस्त और भुगतान संबंधी शर्तें",metadata=[("पत्र संख्या","डीएस/ऋण/2026/075"),("ऋणदाता","जनसेवा वित्त निगम लिमिटेड"),("उधारकर्ता","सीमा वर्मा"),("स्वीकृति तिथि","18 नवंबर 2026"),("मूलधन राशि","₹4,00,000"),("ऋण अवधि","24 महीने")],sections=[("ऋण स्वीकृति","उधारकर्ता को ₹4,00,000 का व्यक्तिगत ऋण स्वीकृत किया जाता है। ₹4,000 का प्रसंस्करण शुल्क और लागू कर वितरण से पहले काटे जाएंगे।"),("ब्याज","घटते मूलधन पर 10.25% की निश्चित वार्षिक दर से ब्याज लिया जाएगा। ब्याज की गणना प्रतिदिन और प्रविष्टि मासिक आधार पर होगी।"),("पुनर्भुगतान","उधारकर्ता ₹18,520 की 24 मासिक किस्तों का भुगतान करेगा। प्रत्येक किस्त हर महीने की 7 तारीख तक देय होगी। पहली किस्त 7 दिसंबर 2026 और अंतिम किस्त 7 नवंबर 2028 को देय होगी।"),("विलंब और चूक","देय तिथि के 5 दिन बाद तक भुगतान न होने पर ₹450 का विलंब शुल्क लगाया जा सकता है। लगातार 2 किस्तों का भुगतान न करना चूक माना जाएगा।"),("पूर्व भुगतान","12 किस्तें पूरी होने के बाद शेष ऋण का पूर्व भुगतान किया जा सकता है। पूर्व भुगतान की गई राशि पर 1.5% शुल्क लग सकता है।"),("शिकायत निवारण","शिकायत प्राप्त होने के 30 दिनों के भीतर उसका निवारण किया जाएगा। समाधान न होने पर उधारकर्ता उपलब्ध वैधानिक उपाय अपना सकता है।")]),
    dict(filename="Financial_HI_02_Masik_Bank_Vivaran.pdf",lang="hi",category="FINANCIAL",code="FIN-HI-02",title="मासिक बचत खाता विवरण",subtitle="अगस्त 2026 के लिए लेनदेन और शेष राशि का विवरण",metadata=[("खाताधारक","रोहित कुलकर्णी"),("खाता संख्या","XXXX XXXX 7315"),("शाखा","नागपुर मुख्य शाखा"),("विवरण अवधि","1 अगस्त 2026 से 31 अगस्त 2026"),("आरंभिक शेष","₹62,500"),("अंतिम शेष","₹71,280")],sections=[("लेनदेन सारांश","नीचे दिए गए लेनदेन नमूना जमा, निकासी, भुगतान और ब्याज प्रविष्टियाँ दर्शाते हैं।"),("महत्वपूर्ण सूचना","किसी अनधिकृत लेनदेन की सूचना विवरण तिथि से 30 दिनों के भीतर दें। खाते में न्यूनतम ₹5,000 का औसत मासिक शेष रखना आवश्यक है।"),("शेष की पुष्टि","31 अगस्त 2026 को खाते में उपलब्ध अंतिम शेष राशि ₹71,280 है।")],tables=[(1,["तिथि","विवरण","नामे (रुपये)","जमा (रुपये)","शेष (रुपये)"],[["02 अगस्त","वेतन जमा","-","55,000","1,17,500"],["05 अगस्त","किराया भुगतान","20,000","-","97,500"],["11 अगस्त","बिजली बिल","2,850","-","94,650"],["17 अगस्त","एटीएम निकासी","8,000","-","86,650"],["25 अगस्त","बीमा प्रीमियम","16,000","-","70,650"],["31 अगस्त","ब्याज जमा","-","630","71,280"]],[24*mm,55*mm,29*mm,29*mm,33*mm])]),
    dict(filename="Legal_EN_01_Residential_Rent_Agreement.pdf",lang="en",category="LEGAL",code="LEG-EN-01",title="RESIDENTIAL RENT AGREEMENT",subtitle="Terms governing possession and use of a residential premises",metadata=[("Agreement ID","DS-RENT-2026-121"),("Landlord","Anita Sharma"),("Tenant","Rohan Nair"),("Premises","Flat 402, Lake View Residency, Pune"),("Commencement","1 December 2026"),("Term","11 months")],sections=[("Rent and deposit","The monthly rent is INR 28,000, payable on or before the 5th day of each month. The Tenant shall pay a refundable security deposit of INR 84,000."),("Permitted use","The premises shall be used only as a private residence. Subletting and commercial activity require prior written consent."),("Maintenance","The Tenant shall pay electricity, internet and routine usage charges. The Landlord remains responsible for structural repairs not caused by the Tenant."),("Inspection","The Landlord may inspect the premises after giving at least 24 hours prior notice, except in an emergency."),("Termination","Either party may terminate this Agreement by giving 30 days prior written notice. Unpaid rent for 15 days after its due date is a material breach."),("Dispute resolution","The parties shall first attempt good-faith settlement. Courts at Pune, Maharashtra have jurisdiction where legally permitted.")]),
    dict(filename="Legal_EN_02_Employment_Service_Agreement.pdf",lang="en",category="LEGAL",code="LEG-EN-02",title="EMPLOYMENT SERVICE AGREEMENT",subtitle="Employment duties, confidentiality and termination conditions",metadata=[("Agreement ID","DS-EMP-2026-209"),("Employer","Civic Data Services Private Limited"),("Employee","Priya Kapoor"),("Position","Document Operations Analyst"),("Start date","15 January 2027"),("Work location","Mumbai, Maharashtra")],sections=[("Appointment and compensation","The Employee is appointed as Document Operations Analyst with a gross monthly salary of INR 72,000, subject to statutory deductions."),("Duties","The Employee shall perform assigned document review, customer support and records-management duties with reasonable skill and care."),("Confidentiality","Confidential information and personal data may be used only for authorised work. This obligation continues after termination."),("Intellectual property","Work product created within assigned duties belongs to the Employer to the extent permitted by law."),("Leave and conduct","Leave is governed by company policy and applicable law. Fraud, harassment, deliberate data misuse, or repeated serious misconduct may result in disciplinary action."),("Termination","Either party may terminate employment by giving 30 days written notice or salary in lieu, subject to applicable law. Disputes shall first be referred to internal grievance review.")]),
    dict(filename="Legal_HI_01_Awas_Kirayanama.pdf",lang="hi",category="LEGAL",code="LEG-HI-01",title="आवासीय किरायानामा",subtitle="आवासीय परिसर के कब्जे, उपयोग और किराया भुगतान की शर्तें",metadata=[("अनुबंध संख्या","डीएस/किराया/2026/144"),("मकान मालिक","सविता देशमुख"),("किरायेदार","अमित पाटिल"),("परिसर","फ्लैट 203, शांतिवन अपार्टमेंट, नासिक"),("प्रारंभ तिथि","1 जनवरी 2027"),("अवधि","11 महीने")],sections=[("कानूनी अनुबंध","यह कानूनी अनुबंध मकान मालिक और किरायेदार नामक पक्षों के अधिकार, दायित्व, समाप्ति, विवाद और न्यायालय संबंधी शर्तें निर्धारित करता है। प्रत्येक पक्ष इस समझौते की धाराओं से बंधा रहेगा।"),("किराया और जमा राशि","मासिक किराया ₹22,000 है, जो प्रत्येक महीने की 5 तारीख तक देय होगा। किरायेदार ₹66,000 की वापसी योग्य सुरक्षा जमा राशि देगा।"),("परिसर का उपयोग","परिसर का उपयोग केवल निजी आवास के लिए किया जाएगा। मकान मालिक की पूर्व लिखित अनुमति के बिना उप-किराया या व्यावसायिक गतिविधि की अनुमति नहीं होगी।"),("रखरखाव","किरायेदार बिजली, पानी और नियमित उपयोग शुल्क देगा। संरचनात्मक मरम्मत का दायित्व मकान मालिक का होगा, यदि क्षति किरायेदार के कारण न हुई हो।"),("निरीक्षण","आपात स्थिति को छोड़कर मकान मालिक कम से कम 24 घंटे पहले सूचना देकर परिसर का निरीक्षण कर सकता है।"),("समाप्ति और विवाद","कोई भी पक्ष 30 दिन पहले लिखित सूचना देकर यह अनुबंध समाप्त कर सकता है। पक्ष पहले आपसी बातचीत से विवाद सुलझाएंगे। नासिक, महाराष्ट्र के न्यायालयों को कानूनन अनुमत अधिकार-क्षेत्र प्राप्त होगा।")]),
    dict(filename="Legal_HI_02_Seva_Anubandh.pdf",lang="hi",category="LEGAL",code="LEG-HI-02",title="व्यावसायिक सेवा अनुबंध",subtitle="सेवा, गोपनीयता, भुगतान और समाप्ति संबंधी शर्तें",metadata=[("अनुबंध संख्या","डीएस/सेवा/2026/318"),("ग्राहक","लोकहित डिजिटल सेवा प्राइवेट लिमिटेड"),("सेवा प्रदाता","नीलम जोशी"),("सेवा","दस्तावेज़ समीक्षा और अभिलेख प्रबंधन"),("प्रभावी तिथि","20 दिसंबर 2026"),("अवधि","12 महीने")],sections=[("कानूनी स्वरूप","यह कानूनी अनुबंध दोनों पक्षों के अधिकार, दायित्व, गोपनीयता, उल्लंघन, समाप्ति, विवाद और उपलब्ध न्यायालय संबंधी शर्तें निर्धारित करता है। दोनों पक्ष इस समझौते की प्रत्येक धारा से बंधे रहेंगे।"),("सेवाओं का दायरा","सेवा प्रदाता दस्तावेज़ समीक्षा, अभिलेख वर्गीकरण और मासिक अनुपालन रिपोर्ट तैयार करेगा। कार्य निर्धारित समय और स्वीकृत निर्देशों के अनुसार किया जाएगा।"),("सेवा शुल्क","ग्राहक प्रत्येक महीने ₹45,000 का सेवा शुल्क देगा। सत्यापित चालान मिलने के 15 दिनों के भीतर भुगतान किया जाएगा और लागू कर कानून के अनुसार काटे जाएंगे।"),("गोपनीयता","सेवा प्रदाता गोपनीय जानकारी और व्यक्तिगत डेटा को सुरक्षित रखेगा तथा केवल अनुबंधित सेवाओं के लिए उपयोग करेगा। यह दायित्व अनुबंध समाप्त होने के बाद भी लागू रहेगा।"),("अभिलेख और लेखापरीक्षा","सेवा से संबंधित अभिलेख 3 वर्षों तक रखे जाएंगे। ग्राहक 5 कार्य दिवस पहले सूचना देकर संबंधित अभिलेखों की जाँच कर सकता है।"),("उल्लंघन और समाप्ति","लिखित सूचना मिलने के 15 दिनों के भीतर गंभीर उल्लंघन का निवारण करना होगा। कोई भी पक्ष 30 दिन पहले लिखित सूचना देकर अनुबंध समाप्त कर सकता है। विवाद का समाधान पहले सद्भावपूर्ण बातचीत से किया जाएगा।")]),
]

if __name__ == "__main__":
    for spec in docs:
        print(create(**spec))
