"""Sends the digest as an HTML email via Gmail SMTP."""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

import markdown

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SENDER_EMAIL, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL

log = logging.getLogger(__name__)

EMAIL_CSS = """
body { font-family: Georgia, serif; max-width: 680px; margin: 40px auto; color: #222; line-height: 1.7; }
h1 { color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 8px; }
h2 { color: #16213e; margin-top: 32px; }
a { color: #0f3460; }
blockquote { border-left: 4px solid #e94560; margin: 0; padding-left: 16px; color: #555; }
hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
.footer { font-size: 12px; color: #999; margin-top: 40px; border-top: 1px solid #eee; padding-top: 12px; }
"""

EMAIL_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>{css}</style></head>
<body>
<h1>🔬 Weekly Science & Tech Digest</h1>
<p style="color:#666; font-size:14px;">Week of {date} &nbsp;|&nbsp; Topics: Nuclear Fusion · Pharma · Biotech · Research Papers</p>
<hr>
{body}
<div class="footer">
  You're receiving this because you set it up. Sources: MIT Technology Review, The Economist,
  Science, Nature, ScienceDaily, arXiv, bioRxiv, and more.<br>
  Powered by OpenAI gpt-4o-mini &amp; GitHub Actions.
</div>
</body>
</html>
"""


def _markdown_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["extra", "nl2br"],
    )


def send_email(digest_markdown: str) -> None:
    html_body = _markdown_to_html(digest_markdown)
    html_full = EMAIL_TEMPLATE.format(
        css=EMAIL_CSS,
        date=date.today().strftime("%B %d, %Y"),
        body=html_body,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Weekly Science & Tech Digest — {date.today().strftime('%b %d, %Y')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    # Plain-text fallback
    msg.attach(MIMEText(digest_markdown, "plain"))
    msg.attach(MIMEText(html_full, "html"))

    log.info("Sending email to %s via Gmail SMTP…", RECIPIENT_EMAIL)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            clean_password = GMAIL_APP_PASSWORD.replace("\xa0", "").replace(" ", "")
            server.login(SENDER_EMAIL, clean_password)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        log.info("Email sent successfully.")
    except Exception as exc:
        log.error("Failed to send email: %s", exc)
        raise
