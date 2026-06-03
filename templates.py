from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup

TRACKING_DOMAIN = "https://email-marketing-with-tracking.onrender.com"
LOGO_PATH = "project atm/Assets/Viewtrip_Logo.jpeg"


# ---------------- FOOTER (REUSABLE) ---------------- #
def footer():
    return """
    <hr>
    <p>
        Best regards,<br>
        Khaleed Taiwo<br>
        Viewtrip Travels<br>
        <b>Phone:</b> 09134490422<br>
        <b>Website:</b>
        <a href="https://viewtrip-react-app-b125.vercel.app/">ViewTrip Travels</a>
    </p>
    """


# ---------------- BASE TEMPLATE ---------------- #
def build_email(html_content, email):

    tracking_pixel = f'<img src="{TRACKING_DOMAIN}/open?email={email}" width="1" height="1" style="display:none;">'

    # inject tracking pixel
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", tracking_pixel + "</body>")
    else:
        html_content += tracking_pixel

    msg = MIMEMultipart("related")

    # IMPORTANT: attach HTML properly
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    # Inline Logo Image Configuration
    try:
        with open(LOGO_PATH, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", "<logo>")
            img.add_header("Content-Disposition", "inline", filename="Viewtrip_Logo.jpeg")
            msg.attach(img)
    except FileNotFoundError:
        print(f"⚠️ Image asset not found at '{LOGO_PATH}'. Sending without embedded header image.")

    return msg


# ---------------- INITIAL EMAIL ---------------- #
def generate_email_html(company, email):

    html = f"""
    <html>
    <body style="font-family: Arial; color: #333;">

        <p>Hello <strong>{company}</strong>,</p>

        <p>I hope this email finds you well.</p>

        <p>We provide standard corporate travel support designed to optimize travel management flows.</p>

        <p>We handle everything from flights, secure logistics, and emergency changes seamlessly.</p>

        <p>Would you be open to a brief 5-minute exploratory sync sometime this week?</p>

        {footer()}

        <img src="cid:logo" width="120">

    </body>
    </html>
    """

    return html


# ---------------- FOLLOW UP 1 ---------------- #
def generate_followup_html(company, email):

    html = f"""
    <html>
    <body style="font-family: Arial; color: #333;">

        <p>Hello <strong>{company}</strong>,</p>

        <p>Just following up on my previous email regarding corporate travel support.</p>

        <p>We can assist with flights, visas, and executive travel management.</p>

        {footer()}

        <img src="cid:logo" width="120">

    </body>
    </html>
    """

    return html


# ---------------- FOLLOW UP 2 ---------------- #
def generate_followup2_html(company, email):

    html = f"""
    <html>
    <body style="font-family: Arial; color: #333;">

        <p>Hi <strong>{company}</strong>,</p>

        <p>Quick check-in regarding your corporate travel needs.</p>

        <p>We can simplify logistics for your upcoming trips.</p>

        <p>Open to a quick conversation?</p>

        {footer()}

        <img src="cid:logo" width="120">

    </body>
    </html>
    """

    return html


# ---------------- FINAL FOLLOW UP ---------------- #
def generate_followup3_html(company, email):

    # FIXED: Removed the stray out-of-context 'ngrok version' string line
    html = f"""
    <html>
    <body style="font-family: Arial; color: #333;">

        <p>Hi <strong>{company}</strong>,</p>

        <p>I haven’t heard back, so I’ll assume now isn’t the right time.</p>

        <p>I’ll pause outreach for now, but feel free to reconnect anytime.</p>

        {footer()}

        <img src="cid:logo" width="120">

    </body>
    </html>
    """

    return html