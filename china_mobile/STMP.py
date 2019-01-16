import smtplib
import email
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail_when_error(Error_text):
    sender = 'echo_shuangshuang@163.com'
    receiver = 'ramsey_leung@163.com'
    smtpserver = 'smtp.163.com'
    username = 'echo_shuangshuang@163.com'
    password = 'liang2770'

    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = sender#发送的邮箱
    msg['to'] = receiver#接收的邮箱
    msg['subject'] = 'Eamil comes from Scrapy'#邮件标题
    content = Error_text#邮件内容
    txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
    msg.attach(txt)

    # try:
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver, '25')
    smtp.login(username,password)
    smtp.sendmail(sender, receiver, msg.as_string())
    print("发送成功！")

    smtp.quit()

