import requests
import re
import json
import os
import time


# 孟慧圆
url_mhy = 'https://www.douyin.com/user/MS4wLjABAAAAqoEDGxqoig3MSnBPJ3_KAokCkC6zxX9RE5eNxFvKdbI'
path = './' 
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Mobile Safari/537.36"
}

urlx = url_mhy

sec_uid = urlx.split('/')[-1]
url = "https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}".format(sec_uid)
resp = requests.get(url, headers=headers)
userinfo = json.loads(resp.text)

name = userinfo['user_info']['nickname']
path_douyin = path+'douyin_video'
if os.path.exists(path_douyin) == False:
    os.mkdir(path_douyin)
path_douyin_user = path_douyin+'/'+name
if os.path.exists(path_douyin_user) == False:
    os.mkdir(path_douyin_user)
else:
    files_name = os.listdir(path_douyin_user)
    for i in files_name:
        os.remove(path_douyin_user+i)

year = [2020,2021,2022]
cursor = []
for y in year:
    for i in range(1,13):
        calc = str(y) + '-'+ str(i) + '-' + '01 00:00:00'
        timeArray = time.strptime(calc, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray)) * 1000
        cursor.append(timeStamp)

for i in range(len(cursor) - 1):
    params = {
        "sec_uid": sec_uid,
        "count": 200,
        "min_cursor": cursor[i],
        "max_cursor": cursor[i+1],
        "_signature": "Sq1xlgAAK2.rxFYl7oQq7EqtcY"
    }
    url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'

    resp = requests.get(url=url, params=params, headers=headers)
    data = json.loads(resp.text)
    awemenum = data['aweme_list']
    num=0
    for item in awemenum:
        title = re.sub('[\/:*?"<>|]','-',item['desc'])
        url = item['video']['play_addr']['url_list'][0]
        path_file_name = path_douyin_user+'/'+name+'-'+str(i)+'-'+str(num)+'-'+title + ".mp4"
        try:
            with open(path_file_name, 'wb') as f:
                f.write(requests.get(url, headers=headers).content)
                print(path_file_name+ "--【保存成功】--")
            num+=1
        except:
            pass
print('全部完成')
os.chdir(path)