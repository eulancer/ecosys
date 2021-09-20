import zmail
import config


def send_mail(Email_title, mail_content):
    server = zmail.server('lingssh@126.com', 'aystxdls')
    mail = {
        'subject': Email_title,  # Anything you want.
        'content_html': [mail_content],
        'attachments': '',  # Absolute path will be better.
    }
    server.send_mail(config.email_list, mail)


def send_mail_trade_date():
    """\\"""
if __name__ == '__main__':
    stock_list_html = "hello"
    subject = "test"
    send_mail(subject, stock_list_html)
