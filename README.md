v2ex daily mission
============

*************

使用python模拟浏览器的行为登陆v2ex并领取每日登陆奖励.

****************

使用的模块有`requests`和`BeautifulSoup`.可以使用`esay_install`或者`pip`快速安装.

1. [Requests documentation](http://docs.python-requests.org/en/latest/)
2. [BeautifulSoup documentation](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)

```
sudo pip install requests
sudo pip install beautifulsoup4
```

if already exist

```
sudo pip install --upgrade requests
sudo pip install --upgrade beautifulsoup4
```

*************************

requests 模块 Session 对象具有非常强大的功能,有 post , get 等常用方法,而且可以保存连接和 cookies.get 方法返回一个连接对象,具有很多属性比如 content,text,status_code等等.
BeautifulSoup 的作用是用来解析 html 的,上面的代码中表单里有一个 'once' 值就是 BeautifulSoup 匹配到的(once的作用等会介绍). find 方法接收一对值,然后返回与之匹配的 HTML tag 的整个 tag 的内容.

***********************

下面正式开始模拟浏览器登陆 v2ex ,通过 firefox 或者 chrome 的开发者工具抓包.(按 F12 进入)

step1:访问 http://www.v2ex.com/signin 填写帐号密码,点击登陆.查看Network,可以看到一个POST方法,提交了一个表单.
![Alt text](http://ww4.sinaimg.cn/large/81d2b157gw1efhpb8c4jqj203w03va9y.jpg)

'u':帐号,'p':密码,'next':总是"/",关键是once,如果在点击登陆之前查看网页源代码并Ctrl+f查找once的话,会发现:
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

然后可以看到一个`领取X铜币`的按钮.点击该按钮,页面没有跳转只是刷新了一下,在抓包工具中看到点击按钮实际请求的网址是`http://v2ex.com/mission/daily/redeem?once=80093`这样的,又有一个once,根据上次的经验应该是服务器返回的随机数.
![Alt text](http://ww4.sinaimg.cn/large/81d2b157jw1efhqd1th4uj20dy03lmxg.jpg)
也就是说我们只要组合出上图的网址get一下就可以了.当然两次的once是不样的.

如果在点击领取按钮之前,查看网页源码的话可以发现
![Alt text](http://ww4.sinaimg.cn/large/81d2b157jw1efhqd141jjj210p06b75h.jpg)

那这样就证实了我们的猜测,第二个once是在我们访问 http://v2ex.com/mission/daily 时服务器返回的随机数.  我们仍然是用BeautifulSoup从网页的HTML源码中匹配到once所在的行,然后提取相关内容,组合成最终需要的网址即可.

```
short_url = make_soup('http://v2ex.com/mission/daily', 'class', 'super normal button')['onclick']
#short_url = "location.href = '/mission/daily/redeem?once=80093'"
```

```
first_quote = short_url.find("'")
last_quote = short_url.find("'", first_quote+1) #str.find(str, beg=0 end=len(string))
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
    print("Sucessful.")
else:
    print("Something wrong.")
```


*************************

##crontab

Use command `crontab -e` add one line to the end.
like `10 8 * * * python /home/yxj/Dropbox/python/v2ex.py >/dev/null 2>&1`
At every 8:10 the script will run automatically.

**********************
