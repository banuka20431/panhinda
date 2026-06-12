
from flask_mail import Message

from app.auth.models import User
from app import app
from datetime import datetime, timezone, timedelta
from app import db, mail, logger
from flask import render_template, url_for

def send_email_confirmation(user: User) -> bool:

    token = user.get_email_verification_token()

    SUBJECT = "Sending confirmation link"


    mail_conf_mail = Message(
        SUBJECT, sender=app.config.get("MAIL_USERNAME"), recipients=[user.email]
    )

    user.email_conf_exp = datetime.now(timezone.utc) + timedelta(minutes=5)

    db.session.commit()    

    __link = f"{app.config.get('APP_URL')}{url_for('auth.verify_email', token=token)}"

    mail_conf_mail.html = render_template(
        "auth/emails/conf_email.html",
        user_name=user.first_name,
        link=__link,
        current_year=datetime.now(timezone.utc).year,
    )

    try:
        mail.send(mail_conf_mail)
        logger.info("auth/routes/send_email_confirmation: sending email containing the link > " + __link)
    except Exception as e:
        logger.error("auth/routes/send_email_confirmation: sending email containing the link > " + __link + " failed")
        logger.debug(e)
        return False
    
    return True


