import smtplib


def send(sender, password, receivers=[], message=''):
    try:
        mail_server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
        # identify ourselves to smtp gmail client
        # mail_server.ehlo()
        # secure our email with tls encryption
        # mail_server.starttls()
        # re-identify ourselves as an encrypted connection
        # mail_server.ehlo()
        mail_server.login(sender, password)
        email = """From: {0}
        To: {1}
        Subject: log analyze file

{2}
        """.format(sender, receivers, message)
        mail_server.sendmail(sender, receivers, email)
        print "Successfully sent email"
    except smtplib.SMTPException:
        print "Error: unable to send email"
    mail_server.quit()