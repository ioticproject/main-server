import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys


def message(subject="IoTIC Notification", text="", img=None, attachment=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    if img is not None:
        if type(img) is not list:
            img = [img]
        for one_img in img:
            img_data = open(one_img, 'rb').read()
            msg.attach(MIMEImage(img_data, name=os.path.basename(one_img)))

    if attachment is not None:
        if type(attachment) is not list:
            attachment = [attachment]

        for one_attachment in attachment:
            with open(one_attachment, 'rb') as f:
                file = MIMEApplication(
                    f.read(),
                    name=os.path.basename(one_attachment)
                )
            file['Content-Disposition'] = f'attachment; filename="{os.path.basename(one_attachment)}"'
            msg.attach(file)
    return msg


def send_confirmation_email(dest_email, dest_name, dest_id):
    smtp = smtplib.SMTP('smtp-mail.outlook.com', port=str(os.environ.get("SMTP_PORT")))

    smtp.ehlo()
    smtp.starttls()

    # if not os.environ.get("ADMIN_EMAIL"):
    #     sys.exit("Could not fetch the admin email.")
    # if not os.environ.get("PASSWORD_EMAIL"):
    #     sys.exit("Could not fetch the email password.")
    smtp.login("iotic.team@outlook.com", os.environ.get("PASSWORD_EMAIL"))

    html = open("send_email/email_registration_template.html", "r").read()
    part = MIMEText(html, "html")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "IoTIC Account Confirmation"
    msg.attach(part)

    host = os.environ["IP"]

    smtp.sendmail('iotic.team@outlook.com',
                dest_email,
                msg.as_string().replace('{username}', dest_name).replace('{user_id}', dest_id).replace('{ip}', host).replace('{port}', '5000'))
    smtp.quit()
