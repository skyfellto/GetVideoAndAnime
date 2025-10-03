import os
import random
import re
import sys
import time
import requests
from tqdm import tqdm

cookies = {}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,ru;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://www.bilibili.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.bilibili.com/bangumi/play/ep249470?from_spmid=666.25.episode.0',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    # 'cookie': "buvid3=E14D891B-0C6B-3A57-9B88-6D9B304FD81356040infoc; b_nut=1758352056; _uuid=A3DF9B1010-6565-232A-1AB9-510C8B5107A44658436infoc; buvid4=DCA1F99D-CB92-761C-BAD3-381C26EE898918149-024071017-4kmaO0RaGuqvYBcxFceFOJ6yuMLy6IEZZ1RcIs92+oST4UDEtLtLvnn98BJ50ToL; buvid_fp=42af4f0023cda6e0ee128d589468d5a5; rpdid=|(k|kY|l~|Yl0J'u~l)Jlk|l); theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; enable_web_push=DISABLE; home_feed_column=5; browser_resolution=1707-791; theme-switch-show=SHOWED; bp_t_offset_480976580=1114897776883269632; DedeUserID=3546787663055070; DedeUserID__ckMd5=358a80a52d4a9867; hit-dyn-v2=1; CURRENT_QUALITY=120; __at_once=8587330714922251022; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTk2MzE5NzAsImlhdCI6MTc1OTM3MjcxMCwicGx0IjotMX0.OoM9J4czAoeM9ilZbXpUufTEW3BFAifhe1hecGFPvkE; bili_ticket_expires=1759631910; SESSDATA=0438c78a%2C1774924770%2C9cf30%2Aa2CjBXY2gbatAVeqzBHP6C20sLyhaEkhv2jmtPGz5n3cN7srINFfJOeUKokUDNXQf_zBESVlBNNldFSUlrYnNOckZVejVyT2Yyb2hMUmF2N3dObWt5RV9vVEp6T3JoVGR0MjcxNThnd2d5RTZLOUVQZlFGQjdVMEY5bG94aHNva2hCYnJwRk9SVnRBIIEC; bili_jct=23426f69904bfa227754127798417a11; timeMachine=0; sid=5byhronl; theme_style=dark; bp_t_offset_3546787663055070=1119052904339079168; b_lsid=10891284B_199A3C2E9FC; CURRENT_FNVAL=4048",
}

param = {}

params = {}

def cookieToJson(cookie_str):
    cookie_pairs = cookie_str.split('; ')

    for pair in cookie_pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies[key] = value

def getSeasonId():
    response = requests.get(url="https://api.bilibili.com/pgc/view/web/simple/season",params=params,cookies=cookies,headers=headers)

    if response.ok:
        season_json = response.json()["result"]["season_id"]
        return season_json
    else:
        print("season_id requested failed")
        return None

def getResponse():

    response = requests.get(url="https://api.bilibili.com/pgc/view/web/ep/list",cookies=cookies,params=params,headers=headers)

    if response.ok:
        print("request successfully")
    else:
        print(f"request failed,code = {response.status_code}")

    return response

def getAnimeInfo(start_ep:int,end_ep:int):
    response = getResponse()
    json_info = response.json()
    id_list = json_info["result"]["episodes"]

    video_list = []
    audio_list = []
    title_list = []
    video_size_list = []
    audio_size_list = []

    season_id = getSeasonId()

    num = start_ep - 1
    count = 0
    for li in id_list:
        if count == num:
            num += 1
            count += 1
            if num > end_ep:
                break

            json_data = {
                'scene': 'normal',
                'video_index': {
                    'bvid': None,
                    'cid': None,
                    'ogv_season_id': season_id,
                    'ogv_episode_id': li["ep_id"],
                },
                'video_param': {
                    'qn': 120,
                },
                'player_param': {
                    'fnver': 0,
                    'fnval': 4048,
                    'drm_tech_type': 2,
                },
                'exp_info': {
                    'ogv_half_pay': True,
                },
            }

            resp = requests.post('https://api.bilibili.com/ogv/player/playview', params=param, cookies=cookies,headers=headers, json=json_data)
            json_resp = resp.json()
            video_url = json_resp["data"]["video_info"]["dash"]["video"][0]["base_url"]
            audio_url = json_resp["data"]["video_info"]["dash"]["audio"][0]["base_url"]
            size_video = json_resp["data"]["video_info"]["dash"]["video"][0]["size"]
            size_audio = json_resp["data"]["video_info"]["dash"]["audio"][0]["size"]
            title_name = li["long_title"]
            title_name = re.sub(r'[\\/:*?"<>|]', '_', title_name)
            video_list.append(video_url)
            audio_list.append(audio_url)
            title_list.append(title_name)
            video_size_list.append(size_video)
            audio_size_list.append(size_audio)

            rad = random.randint(1,3)
            time.sleep(rad)
        else:
            count += 1

    return video_list,audio_list,title_list,video_size_list,audio_size_list

def safeInfo(url,file_name,size):
    req = requests.get(url=url, cookies=cookies, headers=headers,stream=True)
    chunk_size = 1024
    progress_bar = tqdm(
        total=size,
        unit='B',
        unit_scale=True,
        desc=file_name,
        file=sys.stdout,
    )

    if req.ok:
        content = req.iter_content(chunk_size=chunk_size)
        with open(file_name, mode="wb") as f:
            for chunk in content:
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        progress_bar.close()
    else:
        print(f"{file_name} request failed,code = {req.status_code}")

if __name__ == '__main__':
    ep_id = input("请输入ep_id(纯数字): ")
    cookie = input("请输入cookie: ")
    start = input("请输入起始集数: ")
    end = input("请输入结束集数: ")

    cookieToJson(cookie)
    params["ep_id"] = ep_id
    param["csrf"] = cookies["bili_jct"]

    video_collection,audio_collection,title_collection,video_size_collection,audio_size_collection = getAnimeInfo(int(start),int(end))

    for video,audio,title,video_size,audio_size in zip(video_collection,audio_collection,title_collection,video_size_collection,audio_size_collection):
        safeInfo(video,f"{title}_video.m4s",video_size)
        safeInfo(audio,f"{title}_audio.m4s",audio_size)

        os.system(f'ffmpeg.exe -loglevel warning -i "{title}_video.m4s" -i "{title}_audio.m4s" -vcodec copy -acodec copy -y "{title}.mp4"')
        os.remove(f"{title}_video.m4s")
        os.remove(f"{title}_audio.m4s")
