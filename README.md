v2ex daily mission
============

*************

自动登陆v2ex并领取每日登陆奖励.  

****************

To-do-list
-----------

* 成功签到提示信息改进
* 每日领取的金币数
* 连续登陆的天数
* BeautifulSoup --> LXML
* 使用log模块记录日志
* ~~https登陆~~
* crontab定时执行
* 帮多个账户签到
* config模块

使用python模拟浏览器的行为登陆v2ex并领取每日登陆奖励.  

使用的模块有`requests`和`BeautifulSoup`.可以使用`esay_install`或者`pip`快速安装.

1. [Requests documentation](http://docs.python-requests.org/en/latest/)
2. [BeautifulSoup documentation](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)

*************************

import packages:

```
# -*- coding : utf-8 -*-
from bs4 import BeautifulSoup
import requests
```

****************

Simply Usage for requests and BeautifulSoup:

```
# -*- coding : utf-8 -*-
from bs4 import BeautifulSoup
import requests

username = ''  # your v2ex username
password = ''  # your v2ex password
login_url = 'http://v2ex.com/signin'
mission_url = 'http://www.v2ex.com/mission/daily'
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"

headers = {
        "User-Agent" : UA,
        "Host" : "www.v2ex.com",
        "Referer" : "http://www.v2ex.com/signin",
        "Origin" : "http://www.v2ex.com"
        }

v2ex_session = requests.Session()

def make_soup(url,tag,name):
    page = v2ex_session.get(url,headers=headers,verify=False).text
    soup = BeautifulSoup(page)
    soup_result = soup.find(attrs = {tag:name})
    # print soup_result
    return soup_result

once_vaule = make_soup(login_url,'name','once')['value']
print once_vaule

post_info = {
    'u' : username,
    'p' : password,
    'once' : once_vaule,
    'next' : '/'
}

resp = v2ex_session.post(login_url,data=post_info,headers=headers,verify=False)

page = v2ex_session.get(mission_url,headers=headers,verify=False).content
print page
print 'done'
```

requests 模块Session对象具有非常强大的功能,有post,get等常用方法,而且可以保存连接和cookies.get方法返回一个连接对象,具有很多属性比如content,text,status_code等等.  
BeautifulSoup 的作用是用来解析html的,上面的代码中表单你有一个'once'值就是BeautifulSoup匹配到的.find方法接收一对值,然后返回与之匹配的HTML tag的整个tag的内容.  

***********************

下面正式开始模拟浏览器登陆v2ex,通过firefox或者chrome的开发者工具抓包.(按F12进入) 

step1:访问 http://www.v2ex.com/signin 填写帐号密码,点击登陆.查看Network,可以看到一个POST方法,提交了一个表单.  
![Alt text](http://ww4.sinaimg.cn/large/81d2b157gw1efhpb8c4jqj203w03va9y.jpg)

'u':帐号,'p':密码,'next':总是"/",关键是once,查看网页源代码并Ctrl+f查找once发现:  
![Alt text](http://ww4.sinaimg.cn/large/81d2b157jw1efhpi15mjij212c0betb7.jpg)

而且每次都在变化,所以once应该是每一次请求 http://www.v2ex.com/signin 网址时服务器返回的一个随机数.我们用BeautifulSoup找到once的值,填到表单中提交就可以成功登陆了.  

make_suop 函数:

```
def make_soup(url,tag,name):
    page = v2ex_session.get(url,headers=headers,verify=False).text
    soup = BeautifulSoup(page)
    soup_result = soup.find(attrs = {tag:name})
    # print soup_result
    return soup_result
```
soup.find的返回值可以像字典一样使用.则可以拿到once的值了.

```
once_value = make_soup('http://www.v2ex.com/signin', 'name', 'once')['value']
```

组成post_form,然后提交:

```
post_info = {
    'u' : username,
    'p' : password,
    'once' : once_vaule,
    'next' : '/'
}
```

```
resp = v2ex_session.post(login_url,data=post_info,headers=headers,verify=False)
```
headers用来伪装浏览器,verify表示http/https,post之后v2ex_session是可以保存有cookies的,再用v2ex\_session去请求其它网页,是维持登陆状态的.

***********************

在浏览器中我们登陆成功之后,跳转到 http://www.v2ex.com/ 即主页,如果当天你没有签到的话,会看到`领取今日登陆奖励的链接`我们点击该链接,跳转到了 http://www.v2ex.com/mission/daily 请求是这样的. 
![Alt text](http://ww3.sinaimg.cn/large/81d2b157jw1efhqd1i6h5j20at02omx9.jpg)  

然后可以看到一个`领取X铜币`的按钮.点击该按钮,页面没有跳转只是刷新了一下,在抓包工具中看到实际点击按钮请求的网址是`http://v2ex.com/mission/daily/redeem?once=80093`这样的,又有一个once,根据上次的经验应该是服务器返回的随机数.  
![Alt text](http://ww4.sinaimg.cn/large/81d2b157jw1efhqd1th4uj20dy03lmxg.jpg)  
也就是说我们只要,组合出上图的网址get一下就可以了.当然两次的once是不样的.  

如果在点击领取按钮之前,查看网页源码的话可以发现  
![Alt text](http://ww4.sinaimg.cn/large/81d2b157jw1efhqd141jjj210p06b75h.jpg)

那这样就证实了我们的猜测,第二个once是在我们访问 http://v2ex.com/mission/daily 时服务器返回的随机数.  我们仍然是用BeautifulSoup从网页的HTML源码中匹配到once所在的行,然后提取相关内容,组合成最终需要的网址即可.

```
short_url = make_soup('http://v2ex.com/mission/daily', 'class', 'super normal button')['onclick']
#short_url = "location.href = '/mission/daily/redeem?once=80093'"
```

```
first_quote = short_url.find("'")
last_quote = short_url.find("'", first_quote+1) #string的find str.find(str, beg=0 end=len(string))
final_url = "http://www.v2ex.com" + short_url[first_quote+1:last_quote]
# 对short_url进行切片处理 /mission/daily/redeem?once=80093
# final_url = 'http://v2ex.com/mission/daily/redeem?once=80093'
```

请求final_url 

```
page = v2ex_session.get(final_url,headers=headers,verify=False).content
```

检查是否领取成功,领取成功的页面是这样的,

![Alt text](http://ww2.sinaimg.cn/large/81d2b157jw1efhre5gb88j20s206g75t.jpg) 

```
suceessful = make_soup('http://v2ex.com/mission/daily', 'class', 'icon-ok-sign')
if sucessful:
    print "Sucessful."
else:
    print "Something wrong."
```
