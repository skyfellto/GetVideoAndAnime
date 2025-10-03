import json
import os
import re
import requests
from tqdm import tqdm
import sys

cookies = {}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,ru;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.bilibili.com/?spm_id_from=..0.0',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    # 'cookie': "buvid3=E14D891B-0C6B-3A57-9B88-6D9B304FD81356040infoc; b_nut=1758352056; _uuid=A3DF9B1010-6565-232A-1AB9-510C8B5107A44658436infoc; buvid4=DCA1F99D-CB92-761C-BAD3-381C26EE898918149-024071017-4kmaO0RaGuqvYBcxFceFOJ6yuMLy6IEZZ1RcIs92+oST4UDEtLtLvnn98BJ50ToL; buvid_fp=42af4f0023cda6e0ee128d589468d5a5; rpdid=|(k|kY|l~|Yl0J'u~l)Jlk|l); theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; enable_web_push=DISABLE; home_feed_column=5; browser_resolution=1707-791; theme-switch-show=SHOWED; bp_t_offset_480976580=1114897776883269632; DedeUserID=3546787663055070; DedeUserID__ckMd5=358a80a52d4a9867; hit-dyn-v2=1; CURRENT_QUALITY=120; __at_once=8587330714922251022; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTk2MzE5NzAsImlhdCI6MTc1OTM3MjcxMCwicGx0IjotMX0.OoM9J4czAoeM9ilZbXpUufTEW3BFAifhe1hecGFPvkE; bili_ticket_expires=1759631910; b_lsid=1B8FB10B5_199A2CA0230; SESSDATA=0438c78a%2C1774924770%2C9cf30%2Aa2CjBXY2gbatAVeqzBHP6C20sLyhaEkhv2jmtPGz5n3cN7srINFfJOeUKokUDNXQf_zBESVlBNNldFSUlrYnNOckZVejVyT2Yyb2hMUmF2N3dObWt5RV9vVEp6T3JoVGR0MjcxNThnd2d5RTZLOUVQZlFGQjdVMEY5bG94aHNva2hCYnJwRk9SVnRBIIEC; bili_jct=23426f69904bfa227754127798417a11; timeMachine=0; bp_t_offset_3546787663055070=1118987191339450368; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; sid=5byhronl; theme_style=dark; CURRENT_FNVAL=4048",
}

def cookieToJson(cookie_str):
    cookie_pairs = cookie_str.split('; ')

    for pair in cookie_pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies[key] = value

def getResponse(url):
    params = {
        'spm_id_from': '333.1007.tianma.1-1-1.click',
        'vd_source': '239df696922f7437c4c718d878d9260a',
    }

    response = requests.get(url=url, params=params, headers=headers, cookies=cookies)

    if response.ok:
        print("request successfully")
    else:
        print(f"request failed,code = {response.status_code}")

    return response

def getVideoInfo(bvId):
    url = f"https://www.bilibili.com/video/{bvId}"
    response = getResponse(url)
    html = response.text
    find_url = re.compile(r"<script>window.__playinfo__=(.*?)</script>", re.S)
    find_title = re.compile(r"<title>(.*?)</title>", re.S)
    title = find_title.findall(html)[0].split("_哔哩哔哩_bilibili")[0]
    title = re.sub(r'[\\/:*?"<>|]', '_', title)
    json_info = find_url.findall(html)[0]
    json_data = json.loads(json_info)
    # 音频链接
    audio_url = json_data["data"]["dash"]["audio"][0]["baseUrl"]
    # 视频链接
    video_url = json_data["data"]["dash"]["video"][0]["baseUrl"]

    time_length = int(json_data["data"]["timelength"])/1000
    band_width_video = int(json_data["data"]["dash"]["video"][0]["bandwidth"])
    size_video = time_length * band_width_video / 8

    band_width_audio = int(json_data["data"]["dash"]["audio"][0]["bandwidth"])
    size_audio = time_length * band_width_audio / 8

    return audio_url, video_url, title,size_video,size_audio


def saveInfo(url, file_name,size):
    chunk_size = 1024

    progress_bar = tqdm(
        total=size,
        unit='B',
        unit_scale=True,
        desc=file_name,
        file=sys.stdout,
    )

    content = requests.get(url=url, cookies=cookies, stream=True,headers=headers).iter_content(chunk_size=chunk_size)

    with open(file_name, mode="wb") as f:
        for chunk in content:
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
    progress_bar.close()

if __name__ == '__main__':
    bv = input("请输入BV号: ")
    cookie = input("请输入cookie: ")
    cookieToJson(cookie)
    audio, video, title,video_size,audio_size = getVideoInfo(bv)

    saveInfo(audio,f"{title}_audio.m4s",audio_size)
    saveInfo(video, f"{title}_video.m4s",video_size)

    os.system(f'ffmpeg.exe -loglevel warning -i "{title}_video.m4s" -i "{title}_audio.m4s" -vcodec copy -acodec copy -y "{title}.mp4"')
    os.remove(f"{title}_video.m4s")
    os.remove(f"{title}_audio.m4s")