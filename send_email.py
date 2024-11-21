import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr
import os

# 定义发送邮件的函数
def send_email_with_attachments(subject, body, folder_path, smtp_server="smtp.qq.com", smtp_port=465, password="wgxovaofmtyiebbd",sender_email="2505573637@qq.com", receiver_email="18013313704@163.com"):
    try:

        # 连接服务器
        server = smtplib.SMTP_SSL('smtp.qq.com', smtp_port)

        # 登录邮箱
        loginResult = server.login(sender_email, password)

        # 创建一个MIMEMultipart对象，用于构造邮件
        message = MIMEMultipart()

        # 邮件正文
        body = MIMEText(subject, 'plain', 'utf-8')
        message.attach(body)

        # 设置发件人、收件人和主题
        message['From'] = formataddr((str(Header('tyt', 'utf-8')), sender_email))  # 发件人
        message['To'] = formataddr((str(Header('toefl', 'utf-8')), receiver_email))  # 收件人
        message['Subject'] = Header(f'{subject} - 附件', 'utf-8')  # 邮件主题

        # 添加附件
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # 确保是文件，而不是文件夹
            if os.path.isfile(file_path):
                # 打开文件并读取内容
                with open(file_path, 'rb') as attachment:
                    # 构造附件
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={filename}')

                    # 将附件添加到邮件中
                    message.attach(part)

        # 发送邮件
        server.sendmail(sender_email, ["18013313704@163.com"], message.as_string())

        # 关闭文件和服务器连接
        attachment.close()
        server.quit()

    except Exception as e:
        print(f"发送邮件过程中出现错误：{e}")
        return 'error'
    return 'success'


# 使用示例
if __name__ == "__main__":
    # 发件人邮箱地址
    sender_email = "2505573637@qq.com"
    # 收件人邮箱地址
    receiver_email = "18013313704@163.com"
    # 邮件主题
    subject = "Test Email with Attachments"
    # 邮件正文
    body = "This email contains all files from the specified folder."
    # 要发送的文件夹路径
    folder_path = 'results//try'  # 使用 os.path.join 来构建路径

    # QQ邮箱SMTP服务器地址和端口
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # SSL端口587

    # 登录邮箱和授权码（而不是邮箱密码）
    login_email = "2505573637@qq.com"
    password = "wgxovaofmtyiebbd"  # 使用QQ邮箱的授权码

    # 发送邮件
    send_email_with_attachments(subject, body, folder_path)
