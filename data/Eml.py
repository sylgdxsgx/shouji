import logging
import poplib
import smtplib
import email
from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr
from email.header import Header

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class Eml():

    def __init__(self):
        # self.login_status = self.login()
        self.login_status = False
        pass

    def decode_str(self,s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value


    def guess_charset(self,msg):
        # 先从msg对象获取编码:
        charset = msg.get_charset()
        if charset is None:
            # 如果获取不到，再从Content-Type字段获取:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset


    def get_email_headers(self,msg):
        # 邮件的From, To, Subject存在于根对象上:
        headers = {}
        for header in ['From', 'To', 'Subject', 'Date']:
            value = msg.get(header, '')
            if value:
                if header == 'Date':
                    headers['date'] = value
                if header == 'Subject':
                    # 需要解码Subject字符串:
                    subject = self.decode_str(value)
                    headers['subject'] = subject
                else:
                    # 需要解码Email地址:
                    hdr, addr = parseaddr(value)
                    name = self.decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
                    if header == 'From':
                        from_address = value
                        headers['from'] = from_address
                    else:
                        to_address = value
                        headers['to'] = to_address
        content_type = msg.get_content_type()
        # print('head content_type: ', content_type)
        return headers

    # indent用于缩进显示:
    def get_email_cntent(self,message, base_save_path):
        j = 0
        content = ''
        attachment_files = []
        for part in message.walk():
            j = j + 1
            file_name = part.get_filename()
            contentType = part.get_content_type()
            # 保存附件
            if file_name: # Attachment
                # Decode filename
                h = myemail.Header.Header(file_name)
                dh = myemail.Header.decode_header(h)
                filename = dh[0][0]
                if dh[0][1]: # 如果包含编码的格式，则按照该格式解码
                    filename = unicode(filename, dh[0][1])
                    filename = filename.encode("utf-8")
                data = part.get_payload(decode=True)
                att_file = open(base_save_path + filename, 'wb')
                attachment_files.append(filename)
                att_file.write(data)
                att_file.close()
            elif contentType == 'text/plain' or contentType == 'text/html':
                # 保存正文
                data = part.get_payload(decode=True)
                charset = self.guess_charset(part)
                if charset:
                    charset = charset.strip().split(';')[0]
                    # print('charset:', charset)
                    data = data.decode(charset)
                content = data
        return content, attachment_files

    def login(self):
        # 输入邮件地址, 口令和POP3服务器地址:
        # logging.info("    Login To Mail service...")
        emailaddress = 'shigx999@163.com'
        # 注意使用开通POP，SMTP等的授权码
        password = 'a12345678'
        pop3_server = 'pop.163.com'

        # 连接到POP3服务器:
        self.server = poplib.POP3(pop3_server)

        # 可以打开或关闭调试信息:
        # server.set_debuglevel(1)

        # POP3服务器的欢迎文字:
        # print (server.getwelcome())

        # 身份认证:
        try:
            self.server.user(emailaddress)
            self.server.pass_(password)
        except:
            logging.info("-Failure to login to mail service")
            self.login_status = False
            pass
            return False
        logging.info("-Success to login to mail service")
        self.login_status = True
              
        return True

    def checkEmail(self):

        #先登入。每次检查邮件都要登入一遍
        self.login()

        # stat()返回邮件数量和占用空间:
        # messagesCount, messagesSize = server.stat()
        # print ('messagesCount:', messagesCount)
        # print ('messagesSize:', messagesSize)

        # list()返回所有邮件的编号:
        try:
            resp, mails, octets = self.server.list()
        except:
            return False
        # print ('------ resp ------')
        # print (resp) # +OK 46 964346 响应的状态 邮件数量 邮件占用的空间大小
        # print ('------ mails ------')
        # print (mails) # 所有邮件的编号及大小的编号list，['1 2211', '2 29908', ...]
        # print ('------ octets ------')
        # print (octets)

        # 获取最新一封邮件, 注意索引号从1开始:
        length = len(mails)
        for i in range(length,0,-1):
            resp, lines, octets = self.server.retr(i)
            # lines存储了邮件的原始文本的每一行,
            # 可以获得整个邮件的原始文本:
            msg_content = b'\n'.join(lines)
            # 把邮件内容解析为Message对象：
            msg = Parser().parsestr(msg_content.decode('gb18030'))

            # 但是这个Message对象本身可能是一个MIMEMultipart对象，即包含嵌套的其他MIMEBase对象，
            # 嵌套可能还不止一层。所以我们要递归地打印出Message对象的层次结构：

            # print ('---------- 解析之后 ----------')
            base_save_path = '/media/markliu/Entertainment/email_attachments/'
            msg_headers = self.get_email_headers(msg)
            content, attachment_files = self.get_email_cntent(msg, base_save_path)

            # print ('subject:', msg_headers['subject'])
            # print ('from_address:', msg_headers['from'])
            # print ('to_address:', msg_headers['to'])
            # print ('date:', msg_headers['date'])
            # print ('content:', content)
            # print ('attachment_files: ', attachment_files)

            break

        return (msg_headers['subject'],msg_headers['date'],content)

    def send_eml_back(self,title,msg=None):
        sender = "shigx999@163.com"
        receiver = ','.join(["1290693568@qq.com"])   #多个邮件，用逗号隔开的邮件字符串
        smtpserver = "smtp.163.com"
        #发送邮箱的账号密码,此处使用的是qq邮箱和第三方登录的授权码
        username = "shigx999@163.com"
        password = "a12345678"


        '''支持附件'''
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = receiver
        message["Subject"] = u"%s"%title

        #添加正文
        if msg:
            file = open(msg,"rb")
            mail_body = file.read()
            file.close()
            message.attach(MIMEText(mail_body, _subtype="html", _charset="utf-8"))

        #添加附件
        if msg:
            att1 = MIMEApplication(open(msg,'rb').read())
            att1.add_header('Content-Disposition', 'attachment', filename='test_result.html')
            message.attach(att1)

        #可以添加多份附件，像att1一样添加即可
        try:
            smtp = smtplib.SMTP_SSL("smtp.163.com")
            smtp.login(username, password)
            smtp.sendmail(sender, receiver, message.as_string())
            logging.info("-Success：Mail delivery success")
            smtp.quit()
            return True
        except smtplib.SMTPException:
            logging.info("-Error: Mail failure")
            smtp.quit()
            return False
            
    def send_eml(self,title,msg=None,atta=None):
        sender = "shigx999@163.com"
        receiver = ','.join(["1290693568@qq.com"])   #多个邮件，用逗号隔开的邮件字符串
        smtpserver = "smtp.163.com"
        #发送邮箱的账号密码,此处使用的是qq邮箱和第三方登录的授权码
        username = "shigx999@163.com"
        password = "a12345678"


        '''支持附件'''
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = receiver
        message["Subject"] = u"%s"%title

        #添加正文
        if msg:
            mail_body = msg.encode('utf-8')
            message.attach(MIMEText(mail_body, _subtype="html", _charset="utf-8"))
        #添加附件
        if atta:
            att1 = MIMEApplication(open(atta,'rb').read())
            att1.add_header('Content-Disposition', 'attachment', filename='test_result.html')
            message.attach(att1)

        #可以添加多份附件，像att1一样添加即可
        

        try:
            smtp = smtplib.SMTP_SSL("smtp.163.com")
            smtp.login(username, password)
            smtp.sendmail(sender, receiver, message.as_string())
            logging.info("-Success：Mail delivery success")
            smtp.quit()
            return True
        except smtplib.SMTPException:
            logging.info("-Error: Mail failure")
            # raise
            smtp.quit()
            return False

if __name__ == '__main__':
    eml = Eml()
    eml.send_eml('betting result',msg="连续6期没有激活计划，关机.投注结果：0")
