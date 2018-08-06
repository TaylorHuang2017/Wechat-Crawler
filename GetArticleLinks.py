import os
from selenium import webdriver
from lxml import etree
import time
import json
import requests
import redis
import re
import random
import sys
import itchat
import pprint

post = dict()
gzlist = ['shmhweixin','minhangnews','meilixinzhuang2017']
gznamelist = ['上海闵行','闵行报社','美丽莘庄']
text_to_send = ''
url = 'https://mp.weixin.qq.com'
header = {
    "HOST": "mp.weixin.qq.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
}

def send_complex_message(subject, text):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxbc5425db5f0e46be99aa28b2746769d1.mailgun.org/messages",
        auth=("api", "<your api key>"),
        data={"from": "Mailgun Sandbox <postmaster@sandboxbc5425db5f0e46be99aa28b2746769d1.mailgun.org>",
              "to": "<your mailbox address>",
              "subject": subject,
              "text": "Testing some Mailgun awesomeness!",
              "html": text})

def update_cookie():
    driver = webdriver.Edge()
    driver.get('https://mp.weixin.qq.com/')
    time.sleep(1)
    driver.find_element_by_xpath("//input[@name='account']").clear()
    driver.find_element_by_xpath("//input[@name='account']").send_keys('公众号用户名')
    driver.find_element_by_xpath("//input[@name='password']").clear()
    driver.find_element_by_xpath("//input[@name='password']").send_keys('公众号密码')
    driver.find_element_by_class_name("frm_checkbox_label").click()
    time.sleep(3)
    #driver.find_element_by_xpath("//a[@class='btn_login']").click()
    time.sleep(15)
    driver.get('https://mp.weixin.qq.com/')
    cookie_items = driver.get_cookies()
    for cookie_item in cookie_items:
        post[cookie_item['name']] = cookie_item['value']
    cookie_str = json.dumps(post)
    with open('cookie.txt', 'w+', encoding='utf-8') as f:
        f.write(cookie_str)
    driver.quit()

def get_fakeid(parameter):
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    search_response = requests.get(search_url, cookies=cookies, headers=header, params=parameter)
    try:
        search_response.raise_for_status()
        lists = search_response.json().get('list')[0]
        return lists.get('fakeid')
    except Exception as exc:
        print('There was a problem in get_fakeid: %s' % (exc))
        os.system('pause')

def get_articles(parameter):
    global text_to_send
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=parameter)
    try:
        appmsg_response.raise_for_status()

        # max_num = appmsg_response.json().get('app_msg_cnt') 

        fakeid_list = appmsg_response.json().get('app_msg_list')
        fakeid_list = fakeid_list[0:6]

        for item in fakeid_list:
            text_to_send += '  '+ item.get('title') + ' '+'<a href="'+ item.get('link') + '">' + 'Link' + '</a><br><br>'

    except Exception as exc:
        print('There was a problem in get_articles: %s' % (exc))
        os.system('pause')

#itchat.auto_login(hotReload=True)


with open('cookie.txt', 'r', encoding='utf-8') as f:
    cookie_from_file = f.read()
cookies = json.loads(cookie_from_file)
response = requests.get(url=url, cookies=cookies)

try:
    response.raise_for_status()
    token = re.findall(r'token=(\d+)', str(response.url))[0]
except Exception as exec:
    print('cookie has expired: %s' % (exec))
    update_cookie()


for i in range(len(gzlist)):

    query_id = {
        'action': 'search_biz',
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': gzlist[i],
        'begin': '0',
        'count': '5',
    }

    fakeid = get_fakeid(query_id)

    query_id_data = {
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'action': 'list_ex',
        'begin': '0',
        'count': '5',   # 取最新的5条消息
        'query': '',
        'fakeid': fakeid,
        'type': '9'
    }
    text_to_send += '<p><b>' + gznamelist[i] + '</b></p>'
    get_articles(query_id_data)
    text_to_send += "<br>"

send_complex_message("公众号更新:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'<html><head><title>微信公众号</title></head><body>'+ text_to_send + '</body></html>')

sys.exit()


