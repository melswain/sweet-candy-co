# import smtplib, imaplib, email
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from time import sleep
# import fanControl

# # Gmail Info
# sender_email = "kishaan2006@gmail.com"
# sending_app_password = "imntfpdfsbgxacrp"  # App password (no spaces)
# receiver_email = "uselessmayl@gmail.com"
# receiving_app_password = "iagqjihgfsfiwgdo"

# # Sending code
# def sendEmail():
#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = "Test Email from Python"
#     msg["From"] = sender_email
#     msg["To"] = receiver_email
#     msg.attach(MIMEText("Refrigerator is overheating", "plain"))

#     try:
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(sender_email, sending_app_password)
#             server.send_message(msg)
#         print("Email sent successfully!")
#     except Exception as e:
#         print("Sending failed:", e)


# # sleep(10)

# #Reading code
# def readEmail():
#     try:
#         mail = imaplib.IMAP4_SSL('imap.gmail.com')
#         mail.login(sender_email, sending_app_password)
#         mail.select('inbox')

#         data = mail.search(None, 'X-GM-RAW "from:uselessmayl@gmail.com"')
#         ids = data[0].split()
#         latest_email_id = ids[-1]

#         data = mail.fetch(latest_email_id, "(RFC822)")
#         raw_email = data[0][1]
#         msg = email.message_from_bytes(raw_email)

#         print("\n📩 Latest email:")
#         print("From:", msg["From"])
#         print("Subject:", msg["Subject"])

#         if msg.is_multipart():
#             for part in msg.walk():
#                 if part.get_content_type() == "text/plain":
#                     receiver_answer = part.get_payload(decode=True).decode()
#                     clean_answer = receiver_answer.strip().lower()
#                     for line in clean_answer.splitlines():
#                             first_line = line.strip()
#                             break
#                     print(first_line)
#                     if first_line.lower() == "yes":
#                         print("Responded with Yes")
#                         fanControl.turnOnFan()
#                         return True
#                     else:
#                         print(first_line)
#                         print ("Invalid Response OR not Responded")
#                         return False
#         else:
#             print("Body:", msg.get_payload(decode=True).decode())
#             receiver_answer = part.get_payload(decode=True).decode()
#             clean_answer = receiver_answer.strip().lower()
#             for line in clean_answer.splitlines():
#                 first_line = line.strip()
#                 break
#             print(first_line)
#             if first_line.lower() == "yes":
#                         print("Responded with Yes")
#                         fanControl.turnOnFan()
#                         return True
#             else:
#                 print(first_line)
#                 print ("Invalid Response OR not Responded")
#                 return False
                    
#     except Exception as e:
#         print("❌ Receiving failed:", e)

# sendEmail()
# sleep(5)
# readEmail()
# sleep(10)
# fanControl.turnOffFan()

