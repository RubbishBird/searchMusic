
import os, sys, json
import click
import random
import requests, time
from contextlib import closing

'''
Input:
	-mode: search(搜索模式)/download(下载模式)
		--search模式:
			----songname: 搜索的歌名
		--download模式:
			----need_down_list: 需要下载的歌曲名列表
			----savepath: 下载歌曲保存路径
Return:
	-search模式:
		--search_results: 搜索结果
	-download模式:
		--downed_list: 成功下载的歌曲名列表
'''
savepath = r'D:\songs'


class qq():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
            "referer": "http://y.qq.com"
        }
        self.ios_headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46",
            "referer": "http://y.qq.com"
        }
        self.search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
        self.fcg_url = 'http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg'
        self.download_format_url = "http://dl.stream.qqmusic.qq.com/{}{}.mp3?vkey={}&guid={}&fromtag=1"
        self.search_results = {}

    '''外部调用'''

    def get_song(self, mode='search', **kwargs):
        # print(kwargs)
        if mode == 'search':
            songname = kwargs.get('songname')
            self.search_results = self.__searchBySongname(songname)  # 调用搜索歌曲方法
            # print(self.search_results)    #打印搜索结果
            return self.search_results  # 返回搜索结果
        elif mode == 'download':
            kwargs        #打印Kwargs数据
            need_down_list = kwargs.get('need_down_list')
            # singer = need_down_list.values()
            # dict = need_down_list[0]
            singer = need_down_list['singers']
            downed_list = []
            # savepath = kwargs.get('savepath') if kwargs.get('savepath') is not None else 'D:\songs'
            savepath = kwargs.get('savepath') if kwargs.get('savepath') is not None else 'D:\songs'

            # print(kwargs.get(savepath))
            # print("文件存储在：%s" % savepath)
            if need_down_list is not None:
                songmid = need_down_list['song_id']
                media_mid = need_down_list['media_mid']
                download_name = need_down_list['song_name']
                guid = str(random.randrange(1000000000, 10000000000))
                params = {
                    "guid": guid,
                    "format": "json",
                    "json": 3
                }
                fcg_res = requests.get(self.fcg_url, params=params, headers=self.ios_headers)
                vkey = fcg_res.json()['key']
                # for quality in ["A000","M800", "M500", "C400"]:
                for quality in ["M500", "C400"]:
                    download_url = self.download_format_url.format(quality, songmid, vkey, guid)
                    res = self.__download(download_name, download_url, savepath)
                    if res:
                        break
                    print('[qq-INFO]: %s-%s下载失败, 将尝试降低歌曲音质重新下载...' % (time.time(), quality))
                if res:
                    downed_list.append(download_name)
                    print("%s的歌曲: %s ,音乐品质：%s 下载完成" % (singer, song_name, quality))
                    print("文件存储在：%s" % savepath)
                    # time.sleep(2)
            return downed_list
        else:
            raise ValueError('mode in qq().get must be <search> or <download>...')

    '''下载'''

    def __download(self, download_name, download_url, savepath):

        if not os.path.exists(savepath):
            os.mkdir(savepath)
        # savename = '{}'.format(time.time())
        savename = song_name
        savename += '.mp3'
        try:
            print('[qq-INFO]: 正在下载 --> %s' % savename.split('.')[0])
            with closing(requests.get(download_url, headers=self.headers, stream=True, verify=False)) as res:
                total_size = int(res.headers['content-length'])
                if res.status_code == 200:
                    label = '[FileSize]:%0.2f MB' % (total_size / (1024 * 1024))
                    with click.progressbar(length=total_size, label=label) as progressbar:
                        with open(os.path.join(savepath, savename), "wb") as f:  # wb以二进制格式打开一个文件只用于写入，文件存在则将元内容删除
                            for chunk in res.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                                    progressbar.update(1024)
                else:
                    raise RuntimeError('Connect error...')
            return True
        except:
            return False

    '''根据歌名搜索'''

    def __searchBySongname(self, songname):
        params = {
            'w': songname,
            'format': 'json',
            'p': 1,
            'n': 15
        }
        res = requests.get(self.search_url, params=params, headers=self.headers)  # 定义res变量接受请求的响应
        # print(res.json())         #打印请求中的json信息
        results = []
        for song in res.json()['data']['song']['list']:
            media_mid = song.get('media_mid')
            singers = [s.get('name') for s in song.get('singer')]
            singers = ','.join(singers)
            # print(singers)
            album = song.get('albumname')
            songid = song.get('songmid')
            albumLogo = ''
            results.append({
                'song_name': song.get('songname'),
                'singers': singers,
                'media_mid': media_mid,
                'album_name': album,
                'album_logo': albumLogo,
                'song_id': songid,
            })

        return results


'''测试用'''
if __name__ == '__main__':
    qq_downloader = qq()
    flag = 'y'
    while flag == 'y':
        song_name = input("请输入你需要下载的歌曲： ")
        # song_name = "稻香"

        # print(song_name)
        res = qq_downloader.get_song(mode='search', songname=song_name)
        qq_downloader.get_song(mode='download', need_down_list=res[0],savepath=savepath)
        print("------------------------------------------------")
        flag = input("是否继续下载？（y/n）")
