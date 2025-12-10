#  services/email_service.py
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import imaplib, email
from time import sleep

import fanControl

# Gmail Info
# sender_email = ""
# sending_app_password = ""
# receiver_email = ""
# receiving_app_password = ""

# sender_email = ""
# sending_app_password = ""
# receiver_email = ""
# receiving_app_password = ""

def send_receipt_email(receiver_email, subject, html_content):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sending_app_password)
        server.send_message(msg)

    print("Receipt email sent successfully!")


# # Sending code
def sendEmail(fridgeNumber):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test Email from Python"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.attach(MIMEText(f"Refrigerator {fridgeNumber} is overheating", "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sending_app_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Sending failed:", e)


# # sleep(10)

# #Reading code
def readEmail():
    sleep(10)
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(sender_email, sending_app_password)
        mail.select('inbox')

        data = mail.search(None, 'X-GM-RAW "from:uselessmayl@gmail.com"')
        ids = data[0].split()
        latest_email_id = ids[-1]

        data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        print("\n📩 Latest email:")
        print("From:", msg["From"])
        print("Subject:", msg["Subject"])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    receiver_answer = part.get_payload(decode=True).decode()
                    clean_answer = receiver_answer.strip().lower()
                    for line in clean_answer.splitlines():
                            first_line = line.strip()
                            break
                    print(first_line)
                    if first_line.lower() == "yes":
                        print("Responded with Yes")
                        fanControl.turnOnFan()
                        return True
                    else:
                        print(first_line)
                        print ("Invalid Response OR not Responded")
                        return False
        else:
            print("Body:", msg.get_payload(decode=True).decode())
            receiver_answer = part.get_payload(decode=True).decode()
            clean_answer = receiver_answer.strip().lower()
            for line in clean_answer.splitlines():
                first_line = line.strip()
                break
            print(first_line)
            if first_line.lower() == "yes":
                        print("Responded with Yes")
                        fanControl.turnOnFan()
                        return True
            else:
                print(first_line)
                print ("Invalid Response OR not Responded")
                return False
                    
    except Exception as e:
        print("❌ Receiving failed:", e)

# sendEmail()
# sleep(5)
# readEmail()
# sleep(10)
# fanControl.turnOffFan()

