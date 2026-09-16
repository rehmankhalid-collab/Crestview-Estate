import logging
import smtplib
from email.message import EmailMessage

from app.config import Settings
from app.models import Lead

logger = logging.getLogger("crestview.email")


def send_lead_notification(lead: Lead, settings: Settings) -> None:
    """Email the sales team about a new lead.

    TODO: fill in real SMTP_* values in .env before launch (see
    .env.example). Until then this is a no-op so lead submission still
    works end-to-end in development.
    """
    if not settings.smtp_host:
        logger.info(
            "SMTP not configured (SMTP_HOST empty) — skipping email for lead #%s. "
            "Lead was still saved to the database.",
            lead.id,
        )
        return

    message = EmailMessage()
    message["Subject"] = f"New Crestview Estates lead: {lead.name}"
    message["From"] = settings.smtp_from_email
    message["To"] = settings.lead_notification_email
    message.set_content(
        "A new lead was submitted on the Crestview Estates site.\n\n"
        f"Name: {lead.name}\n"
        f"Phone: {lead.phone}\n"
        f"Submitted: {lead.created_at.isoformat()}\n"
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except (smtplib.SMTPException, OSError):
        # A failed notification email should never fail the lead submission
        # itself — the lead is already safely persisted in the database.
        logger.exception("Failed to send lead notification email for lead #%s", lead.id)
