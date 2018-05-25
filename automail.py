#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import sys, smtplib, pathlib
from email.mime.text import MIMEText

# 第三方 SMTP服务的机密配置，替换以下信息，写入本地文件，保存名为smtp.config
mail_host="xxx"        #设置服务器
mail_port=000          #端口号
mail_user="xxx"        #用户名
mail_pass="xxx"        #口令 
mail_tooo="xxx"        #接收邮件地址，可用于测试

# 邮件相关机密配置文件信息导入
exec(pathlib.Path('smtp.config').read_text())
for v in filter(lambda x: x.find('mail_') == 0, dir()): print(v, '=', eval(v))

def send(message):
    sender = mail_user
    message['From'] = sender
    receivers = message['To'].split(';') + message['Cc'].split(';')

    #update message header
    message.replace_header('Subject', '[AUTO] {}'.format(message['Subject']))
    print(type(message), message.as_string())
    #return

    try:
        smtpObj = smtplib.SMTP(mail_host, mail_port)
        #smtpObj.ehlo()
        #smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件", file=sys.stderr, flush=True)

    return

if __name__ == '__xxmain__':
    message = MIMEText('Python 邮件发送测试...')#, 'plain', 'utf-8')
    message['To'] = mail_tooo   #yourname@example.com
    message['Cc'] = ''
    message['Subject'] = 'Python SMTP Test'

    send(message)   #send test

def send_mail(head, context):
    message = MIMEText(context)#, 'plain', 'utf-8')
    for n, v in head.items():
        message.add_header(n, v)

    #print(type(message), message.as_string())
    send(message)
    return

if __name__ == '__main__':
    send_mail({
            'To' : mail_tooo,   #yourname@example.com
            'Cc' : '',
            'Subject' : 'Python SMTP Test',
        }, '''
Python 邮件发送测试...
        ''')
