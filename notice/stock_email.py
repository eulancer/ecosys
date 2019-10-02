import zmail


def stock_mail(mail_content):
    server = zmail.server('lingssh@126.com', 'aystxdls')
    mail = {
        'subject': 'Success!',  # Anything you want.
        'content_html': [mail_content],
        'attachments': '',  # Absolute path will be better.
    }
    server.send_mail('lingssh@126.com', mail)


if __name__ == '__main__':
    stock_list_html = "hello"
    stock_mail(stock_list_html)
