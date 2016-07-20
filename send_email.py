import smtplib

sender = '***@***.com'
receivers = ['***@qq.com']

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
   mail_server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
   # identify ourselves to smtp gmail client
   # mail_server.ehlo()
   # secure our email with tls encryption
   # mail_server.starttls()
   # re-identify ourselves as an encrypted connection
   # mail_server.ehlo()
   mail_server.login(sender, 'password')
   mail_server.sendmail(sender, receivers, message)
   print "Successfully sent email"
except smtplib.SMTPException:
   print "Error: unable to send email"
