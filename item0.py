#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import sys, smtplib, pathlib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# 请您正确替换第三方 SMTP服务配置的机密信息，存入当前目录，文件名为smtp.config
########################################
mail_host="smtp.xxx.com"        #设置服务器
mail_port=465          #端口号
mail_user="lian.zhulin@gmail.com"        #用户名
mail_pass="xxxczofzsmpsoxxx"        #口令
mail_tooo="lian.zhulin@gmail.com"        #接收邮件地址，可用于测试
########################################

# 从smtp.config文件导入邮件配置信息
exec(pathlib.Path('smtp.config').read_text())
for v in filter(lambda x: x.find('mail_') == 0, dir()): print(v, '=', eval(v))

def send(message):
    sender = mail_user
    message['From'] = sender
    receivers = message['To'].split(';') + message['Cc'].split(';')

    message['Date'] = formatdate(localtime=True)

    #update message header
    message.replace_header('Subject', '[AUTO] {}'.format(message['Subject']))
    print(type(message), message.as_string())
    #return

    '''
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("elastos_whitepaper.pdf", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename="elastos_whitepaper.pdf")
    message.attach(part)
    '''

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        #smtpObj.ehlo()
        #smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件", e, file=sys.stderr, flush=True)

    return

def send_mail(head, context):
    message = MIMEMultipart()#, 'plain', 'utf-8')
    for n, v in head.items():
        #message[n] = v
        message.add_header(n, v)

    message.attach(MIMEText(context, 'plain'))
    send(message)
    return

if __name__ == '__main__':
    send_mail({
            'To' : mail_tooo,   #yourname@example.com
            'Cc' : '',
            'Bcc' : '',
            'Subject' : 'Python SMTP Test',
        }, '''
Python 邮件发送测试...
        ''')
