from __future__ import unicode_literals
from threading import Timer
from wxpy import *
import requests


bot = None
def get_news():
 #获取一个连接中的内容
 url = "http://open.iciba.com/dsapi/"
 r = requests.get(url)
 print(r.json())
 contents = r.json()['content']
 translation = r.json()['translation']
 return contents,translation

def login_wechat():
 global bot
 bot = Bot()
 # bot = Bot(console_qr=2,cache_path="botoo.pkl")#linux环境上使用

def send_news():
 if bot == None:
  login_wechat()
  bot.my_friend = bot.friends().search(u'传输助手')[0] #xxx表示微信昵称
  bot.my_friend.send('Hello WeChat!')
  t = Timer(360, send_news) #360是秒数
  t.start()

if __name__ == "__main__":
 send_news()
 print(get_news()[0])



