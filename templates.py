import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

# Unified tracking URL route matching your server configuration
TRACKING_DOMAIN = "https://email-marketing-with-tracking.onrender.com/track"
LOGO_PATH = "Viewtrip_Logo.jpeg"


# ---------------- FOOTER (REUSABLE) ---------------- #
def footer():
    return """
    <hr style="border:0; border-top: 1px solid #E2E8F0; margin-top:30px;">
    <p style="font-size: 13px; color: #718096; line-height: 1.5;">
        Best regards,<br>
        <strong>Khaleed Taiwo</strong><br>
        Viewtrip Travels<br>
        <b>Phone:</b> 09134490422<br>
        <b>Website:</b> <a href="https://viewtrip-react-app-b125.vercel.app/" style="color: #2B6CB0; text-decoration: none;">ViewTrip Travels</a>
    </p>
    """


# ---------------- TRACKING-SAFE MULTIPART ENGINE ---------------- #
def build_email(html_content, email, attachment_path=None):
    # 1. Top Outer Container (mixed) to house the main email body and optional attachments
    msg_outer = MIMEMultipart("mixed")

    # 2. Middle Container (related) to bundle the text body and the inline image logo
    msg_related = MIMEMultipart("related")
    msg_outer.attach(msg_related)

    # 3. Inner Container (alternative) strictly dedicated to text structures and tracking
    msg_alternative = MIMEMultipart("alternative")
    msg_related.attach(msg_alternative)

    # Inject the unique dynamic tracking image route safely at the bottom of the body text
    tracking_pixel = f'<img src="{TRACKING_DOMAIN}?email={email}" width="1" height="1" style="display:none !important; visibility:hidden; opacity:0;">'

    if "</body>" in html_content:
        html_content = html_content.replace("</body>", tracking_pixel + "</body>")
    else:
        html_content += tracking_pixel

    # Attach the finalized HTML tracking structure to the alternative text part
    html_part = MIMEText(html_content, "html")
    msg_alternative.attach(html_part)

    # Bind your local Inline Logo image into the middle related container section
    if os.path.exists(LOGO_PATH) and os.path.isfile(LOGO_PATH):
        try:
            with open(LOGO_PATH, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-ID", "<logo>")
                img.add_header("Content-Disposition", "inline", filename="Viewtrip_Logo.jpeg")
                msg_related.attach(img)
        except Exception as e:
            print(f"⚠️ Logo image binding warning: {e}")
    else:
        print(f"⚠️ Image asset not found at '{LOGO_PATH}'. Logo placeholder will skip streaming.")

    # Bind your local Corporate Review PDF attachment into the outer mixed container section
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="pdf")
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(attachment_path)
                )
                msg_outer.attach(part)
        except Exception as e:
            print(f"⚠️ Failed to bind PDF document layout attachment: {e}")

    return msg_outer


# ---------------- INITIAL EMAIL ---------------- #
def generate_email_html(company, email):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 10px;">

        <div style="border-bottom: 2px solid #1A365D; padding-bottom: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 22px; font-weight: bold; color: #1A365D;">Viewtrip Travels</span>
            <img src="cid:logo" alt="Viewtrip Logo" style="max-height: 50px; max-width: 150px; object-fit: contain;">
        </div>

        <p>Dear {company},</p>

        <p>My name is Khaleed, and I represent Viewtrip Travels.</p>

        <p>Managing corporate travel is rarely just about booking a flight; it’s about what happens when things don't go as planned. Last-minute cancellations, sudden itinerary changes, and protocol delays can disrupt operations and impact your bottom line.</p>

        <p>We specialize in managing end-to-end travel logistics for corporate entities, ensuring that your team’s focus remains on core operations while we handle the complexities of global and domestic movement.</p>

        <p>Beyond standard bookings, we provide:</p>
        <ul style="list-style-type: none; padding-left: 20px;">
            <li style="margin-bottom: 8px;"><strong>• Strategic Itinerary Planning:</strong> Optimizing routes to reduce travel time and cost.</li>
            <li style="margin-bottom: 8px;"><strong>• End-to-End Visa Management:</strong> Specialized support for technical crews and executive teams.</li>
            <li style="margin-bottom: 8px;"><strong>• 24/7 Priority Support:</strong> Real-time assistance for last-minute changes or flight disruptions.</li>
            <li style="margin-bottom: 8px;"><strong>• Premium Hotel Procurement:</strong> Curated bookings with guaranteed Late Check-in and flexible cancellation policies—essential for shifting project timelines.</li>
            <li style="margin-bottom: 8px;"><strong>• Seamless Ground Support:</strong> Secure, pre-vetted Airport Transfers and point-to-point ground transport, ensuring your team is never left waiting upon arrival.</li>
        </ul>

        <p>I’ve been following {company}’s growth in the industry sector and would welcome the opportunity to discuss how our tailored Travel solutions can drive efficiency for your upcoming 2026 travel calendar.</p>

        <p><em>Please find our complete <strong>Corporate Review Brief</strong> attached to this email for your convenience.</em></p>

        <p>Are you available for a brief introductory call?</p>

        {footer()}
    </body>
    </html>
    """
    return html


def generate_followup_html(company, email):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 10px;">
        <div style="border-bottom: 2px solid #1A365D; padding-bottom: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 22px; font-weight: bold; color: #1A365D;">Viewtrip Travels</span>
            <img src="cid:logo" alt="Viewtrip Logo" style="max-height: 50px; max-width: 150px; object-fit: contain;">
        </div>

        <p>Hi team at {company},</p>
        <p>I wanted to follow up on my previous note regarding optimizing your 2026 travel configuration. I know operational schedules can be demanding.</p>
        <p>Many corporate teams we partner with tell us that handling <strong>Technical Crew Visa Management</strong> and arranging secure, pre-vetted <strong>Airport Transfers</strong> manually eats up hours of their internal operations time.</p>
        <p>Viewtrip Travels absorbs that friction entirely so your field executives and engineers can land and get straight to work without logistical delays.</p>
        <p>Would you have 5 minutes for a quick introductory exchange sometime this week?</p>

        {footer()}
    </body>
    </html>
    """
    return html


def generate_followup2_html(company, email):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 10px;">
        <div style="border-bottom: 2px solid #1A365D; padding-bottom: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 22px; font-weight: bold; color: #1A365D;">Viewtrip Travels</span>
            <img src="cid:logo" alt="Viewtrip Logo" style="max-height: 50px; max-width: 150px; object-fit: contain;">
        </div>

        <p>Hi team,</p>
        <p>Quick check-in regarding travel overhead at {company}.</p>
        <p>When project timelines shift unexpectedly, standard hotel bookings become a liability due to rigid cancellation penalties. Our logistics framework solves this by procuring custom business hotel accounts that guarantee <strong>Late Check-ins</strong> and highly flexible modification windows.</p>
        <p>I would be glad to share a quick 1-page summary of how we mitigate these specific travel Markups for logistics-focused operations.</p>
        <p>Should I drop that over to this address, or is there a better point of contact on your administrative team to review it?</p>

        {footer()}
    </body>
    </html>
    """
    return html


def generate_followup3_html(company, email):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 10px;">
        <div style="border-bottom: 2px solid #1A365D; padding-bottom: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 22px; font-weight: bold; color: #1A365D;">Viewtrip Travels</span>
            <img src="cid:logo" alt="Viewtrip Logo" style="max-height: 50px; max-width: 150px; object-fit: contain;">
        </div>

        <p>Hi team,</p>
        <p>Closing the loop on this from my end. If streamlining your corporate logistics or protecting your 2026 travel budget from cancellation overhead isn't an active priority for {company} right now, I completely understand.</p>
        <p>If your travel requirements scale up or last-minute flight disruptions start creating issues later this year, you can reach out to us directly through this thread.</p>
        <p>Wishing your team a highly productive and successful quarter ahead.</p>

        {footer()}
    </body>
    </html>
    """
    return html