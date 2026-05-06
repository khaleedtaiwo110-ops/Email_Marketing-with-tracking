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

    # attach logo
    try:
        with open(LOGO_PATH, "rb") as img_file:
            mime_img = MIMEImage(img_file.read())
            mime_img.add_header("Content-ID", "<logo>")
            mime_img.add_header("Content-Disposition", "inline", filename="logo.jpg")
            msg.attach(mime_img)
    except FileNotFoundError:
        print("⚠️ Logo not found")

    return msg


# ---------------- INITIAL EMAIL ---------------- #
def generate_email_html(company, email):

    html = f"""
    <html>
    <body style="font-family: Arial; line-height: 1.6; color: #333;">

        <p>Dear <strong>{company}</strong> team,</p>

        <p>My name is Khaleed Taiwo, and I represent <b>Viewtrip Travels</b>.</p>

        <p>We specialize in managing end-to-end travel logistics for corporate entities.</p>

        <ul>
            <li>Strategic Itinerary Planning</li>
            <li>Visa Support</li>
            <li>24/7 Emergency Assistance</li>
            <li>Hotel & Transport</li>
        </ul>

        <p>Would love to explore how we can support {company}.</p>

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

    html = f"""
    <html>
    <body style="font-family: Arial; color: #333;">

        <p>Hi <strong>{company}</strong>,</p>

        <p>I haven’t heard back, so I’ll assume now isn’t the right time.</p>
ngrok version
        <p>I’ll pause outreach for now, but feel free to reconnect anytime.</p>

        <p>Wishing you continued success.</p>

        {footer()}

        <img src="cid:logo" width="120">

    </body>
    </html>
    """

    return html