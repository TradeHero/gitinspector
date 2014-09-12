#!/usr/bin/python

import datetime
from datetime import datetime
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()

server.login(os.environ['SMTP_EMAIL'], os.environ['SMTP_PASSWORD'])

target_email = "dominic@tradehero.mobi"
msg = MIMEMultipart()
msg["From"] = os.environ['SMTP_EMAIL']
msg["To"] = target_email
msg["Date"] = formatdate(localtime=True)
msg["Subject"] = "Git report generated on " + str(datetime.now())

msg.attach( MIMEText("This is an automated email") )

part = MIMEBase('application', "octet-stream")
part.set_payload( open("report.xls", "rb").read())
Encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="report.xls"')
msg.attach(part)

server.sendmail(os.environ['SMTP_EMAIL'], target_email, msg.as_string())

server.quit()
