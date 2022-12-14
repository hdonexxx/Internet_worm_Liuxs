from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import json
import time
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor  # 线程池执行者


#  创建文件夹
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        pass


#合并之后删除下载的ts文件
def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)


# 合并ts文件
def merge_ts_video(ts_path, save_path):
    print(save_path)
    all_ts = os.listdir(ts_path)
    all_ts.sort(key=lambda x: int(x[:-3].split('-')[1]))
    now_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    save_path_new = save_path[:save_path.rfind('.')] + now_time + save_path[
        save_path.rfind('.'):]
    try:
        with open(save_path_new, 'wb+') as f:
            for i in range(len(all_ts)):
                ts_video_path = os.path.join(ts_path, all_ts[i])
                f.write(open(ts_video_path, 'rb').read())
        print('保存文件：', save_path_new)
    except:
        save_path_new = now_time + save_path[save_path.rfind('.'):]
        with open(save_path_new, 'wb+') as f:
            for i in range(len(all_ts)):
                ts_video_path = os.path.join(ts_path, all_ts[i])
                f.write(open(ts_video_path, 'rb').read())
        print('保存文件：', save_path_new)
    print('合并完成')
    del_file(ts_path)
    print('删除原有的碎片ts文件')


# 获取二级链接
def get_user_url(url):
    session = requests.Session()
    r18 = session.get(url, headers=headers)

    r18.raise_for_status()
    r18.encoding = r18.apparent_encoding
    r18.encoding = 'utf-8'
    soup18 = BeautifulSoup(r18.text, 'html.parser')  # 网页信息格式处理
    title = str(soup18.find_all('title')[0]).split('>')[1].split('|')[0]
    title = re.sub('[ /, \, :, *, ?, ", <, >, |]', '-', title)
    print('title',title)
    lines = r18.text.splitlines()

    pieceUrlList = []
    for line in lines:
        if 'contentUrl' in line and 'm3u8' in line:
            pieceUrlList.append(line)

    contentUrl = 'https:' + pieceUrlList[0].split('contentUrl": "')[1][:-2]
    contentUrl = contentUrl.replace(
        '_definst_/mp4:ttp://flv14.afreecatv.com/save/',
        '_definst_/smil:save/').replace('.mp4/playlist.m3',
                                        '.smil/playlist.m3')

    r3 = session.get(contentUrl, headers=headers)
    for i in r3.text.split('\n'):
        if 'playlist.m3u8' in i:
            contentUrl_mess = i
            break
    url_sta = 'https://vod-normal-global-cdn-z02.afreecatv.com' + contentUrl_mess.replace(
        'playlist.m3u8', '')
    # 清晰度修正为原画清晰度
    url_sta = url_sta.replace('hd2k','original').replace('hd','original')

    return url_sta, title


# 构造单个ts文件下载函数，用于多线程下载
def save_ts_video(temporary_file, url_sta, ts_name):
    path_file_ts = temporary_file + ts_name
    if os.path.exists(path_file_ts):
        print('已有文件：', ts_name)
        pass
    else:
        print('正在下载：', ts_name)
        ts_one_url = url_sta + ts_name
        r = requests.get(ts_one_url)
        with open(path_file_ts, 'wb') as code:
            code.write(r.content)
            code.flush()


# 下载所有ts文件
def Down_afreeca_video(url_sta, video_path=''):
    temporary_file = video_path + processfile
    mkdir(temporary_file)
    try:
        m3u8_url = url_sta + 'playlist.m3u8'
        r = requests.get(m3u8_url)
        r.raise_for_status()
    except:
        m3u8_url = url_sta.replace('normal', 'archive') + 'playlist.m3u8'
        r = requests.get(m3u8_url)
        r.raise_for_status()
    r.encoding = r.apparent_encoding
    soup2 = BeautifulSoup(r.text, 'html.parser')  # 网页信息格式处理
    ts_list = []
    for i in str(soup2).split('\n'):
        if 'seg' in i and 'ts' in i:
            ts_list.append(i)
    print('共有{}个文件需下载'.format(len(ts_list)))
    # 创建线程池，最多维护10个线程
    threadpool = ThreadPoolExecutor(10)
    for ts_name in ts_list:
        threadpool.submit(save_ts_video, temporary_file, url_sta, ts_name)
    threadpool.shutdown(True)  # 等待线程池中的任务执行完毕后，在继续执行
    print("下载完成ts文件")
    
# 网页编号修正为网页地址
def get_website(urlx):
    if len(str(urlx))==8:
        urlx = 'https://vod.afreecatv.com/player/'+str(urlx)
    else:
        pass
    return urlx

processfile = 'ts_video18/'
headers = {
    'Cookie':
    'OAX=0gxQMmLgl+0ACK0L; _au=078f9cee6a93943d0c370a1e1b01ec48; bjStationHistory=%0217041065; _gid=GA1.2.2016727917.1661419950; _ga_5EYT9PM505=GS1.1.1661419989.2.1.1661420288.0.0.0; AbroadChk=OK; AbroadVod=OK; availableChinaLayer=1; PdboxTicket=.A32.7bbT56vyHM9fKZk.j2scLRsW2x9VoiFV32R2M0LvOPwh5422MpFzUMNNWnMLFsp2fJkOs3Zt2IdO08ChWYd3ncKX9GGxLGiJ_0H9He8Poe4fbN_3HymJK0zjB4-iMjK9K0WppwWdUx1EtiCfuHPhoZHrdJnhd54-4LoOmEk3SzulnjZR_hal7XR1AVHL6k0AEU_uAKdChqmr2Wc_UCkhfzo9TyAi1yjvksX_FsqSquVXX6E1XntA6HjBVD7FwcEomAAO1iEekYI4as_GKqJH1BcXZX7J5kbQTWiY_UWhmQ-YPZOyaRWJmah1LAxLIa4qTwqlI0gcjyJIlw7wF0e6R4EoBDvXcdwz1w4HCXVKuGk5Ma1aJv63sSw3-ZIRKF53bt38zoo2iDi1Mm2PJBv-I-_PFK7GpwDhjvyOZwbK7MvQoMy3z2Q8MGN95FpFMnQoDLoMlyIXwVw8nTm-vUW8SIPaqR-o3MmPY5i7XghmZxkdmt9150iEDkX2TpBtWJswmPHqEypAfFLLYHQAunWCWeGgDcdU4oBMabmgkuhirm7yNijFC-1I2O5wsQQ; PdboxBbs=hundanone; PdboxUser=uid%3Dhundanone%26uno%3D44233699%26age%3D22%26sex%3DA%26A%3DAAC%26B%3DBACC%26unick%3Dhundanone%26apply_date%3D1633857950%26name_chk%3D1%26sess_adult_chk%3D1%26broad_name_chk%3D1%26change_password%3D%26chnnl_cd%3D18%26chnnl_name_chk%3D1; isBbs=1; RDB=c8030000000000434e0000000000000000000000000000000100000016160000000000000001; _ga=GA1.1.904974892.1658886125; _ausa=0x951926be; _ausb=0x1044732e; _ga_9PY781H32Y=GS1.1.1661486145.15.1.1661486468.58.0.0; VIN=path_key%3D078f9cee6a93943d0c370a1e1b01ec48_83762567_1661486466647%26path1%3Dreload',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}
#保存路径
video_path=''

if __name__ =='__main__':
    # 传入视频网址或者网址末尾编号
    urlx=90425866
    url_sta,title = get_user_url(get_website(urlx))
    Down_afreeca_video(url_sta, video_path)
    merge_ts_video(video_path + processfile, video_path + title + '.mp4')