from urllib import request
from http import cookiejar
import ssl
import urllib.parse
import time
import json
import shutil
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')


login_url = 'https://www.zlfund.cn/accounts/login/'
captcha_url = 'https://www.zlfund.cn/captcha/refresh'
#可以考虑存储下来
cookie = {}
def build_opener():
    ssl._create_default_https_context = ssl._create_unverified_context
    cookie = cookiejar.CookieJar()
    #利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
    handler=request.HTTPCookieProcessor(cookie)
    #通过CookieHandler创建opener
    opener = request.build_opener(handler)
    return opener

def build_default_header():
    headers = {}
    headers['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    headers['Connection']='keep-alive'
    headers['Referer'] = 'https://www.zlfund.cn'
    headers['Origin']='https://www.zlfund.cn'
    headers['X-Requested-With']='XMLHttpRequest'
    return headers


def get_csrftoken():
    opener = build_opener()
    req1 = request.Request(url=login_url, headers=build_default_header())
    response = opener.open(req1)
    html = response.read().decode('utf-8')
    csrftoken = ''
    for item in cookie:
        if(item.name == 'csrftoken'):
            csrftoken = item.value
    return csrftoken



def download_captcha_img(csrftoken):
    headers=build_default_header()
    headers['X-Requested-With']='XMLHttpRequest'
    headers['X-CSRFToken']=csrftoken
    opener=build_opener()

    req_captcha = request.Request(url=captcha_url, headers=build_default_header())
    response = opener.open(req_captcha)
    resp_captcha = response.read().decode('utf-8')
    resp_captcha_json = json.loads(resp_captcha);

    image_url = resp_captcha_json['image_url']

    key = resp_captcha_json['key']

    captcha_img_url = "https://www.zlfund.cn" + image_url

    req_img_captcha = request.Request(url=captcha_img_url, headers=headers)
    img = opener.open(req_img_captcha)
    with open('d:\\captcha.png', "wb") as f:
        shutil.copyfileobj(img, f)

    return key


def do_login(userName,password):
    csrftoken = get_csrftoken()
    key = download_captcha_img(csrftoken)
    captcha_1 = input('请输入验证码:')
    print('验证码：' + captcha_1)
    data={
       'identity':userName,
       'password':password,
       'csrfmiddlewaretoken':csrftoken,
       'captcha_1':captcha_1,
       'captcha_0':key,
       'opseq_serialno':'201802060812242700242'
       }
    headers=build_default_header()
    headers['X-CSRFToken']=csrftoken
    opener = build_opener()
    encodeData = bytes(urllib.parse.urlencode(data), encoding='utf8')
    req2 = request.Request(url=login_url,data=encodeData,headers=headers)
    response = opener.open(req2)
    print(response.getcode())
    html = response.read().decode('utf-8')
        #print(html)

    url = 'https://www.zlfund.cn/accounts/profile/?_='+str(int(round(time.time() * 1000)))

        #替换headerrefer
    headers['Referer'] = 'https://www.zlfund.cn/trade/'
    req3 = request.Request(url=url, headers=headers)
    response = opener.open(req3)
    html = response.read().decode('utf-8')
    print(json.loads(html))



if __name__ == '__main__':
    startTime = time.time()
    userName = input('请输入用户名:')
    print('用户名：' + userName)
    password = input('请输入密码:')
    print('密码：'+ password)
    do_login(userName,password)
    endTime = time.time()
    print ('Done, Time cost: %s ' %  (endTime - startTime))
