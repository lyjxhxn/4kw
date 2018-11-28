import requests
import re
import os
import time
import threadpool


pool = threadpool.ThreadPool(10)
class Run():
    def __init__(self):
       
        path = "E:\\4K屋"
        if not os.path.exists(path):
            os.makedirs(path)
        self.host_url = "http://www.kkkkmao.com"
        self.head = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}

    def get_search(self,name):
        
        url1 = "http://www.kkkkmao.com/index.php?s=plus-search-vod&q=%s"%name
        search_html = requests.get(url1,headers = self.head).json()
        search_data = search_html.get("data")
        if search_data:
            n = 0
            for i in search_data:
                name = i.get("vod_name").replace('<em>/</em>','')
                print(str(n)+"\t"+name)
                n += 1
            while True:
                    try:
                        a = input('请输入电影或电视剧的编号：')
                        a = int(a)
                    except:
                        print('你的输入有误')
                    else:
                        if a < n and a >= 0:
                            break
                        else:
                            print('你的输入有误')
            global vod_name
            html_url = self.host_url + search_data[a].get('vod_url')
            vod_name = search_data[a].get("vod_name").replace('<em>/</em>','').split(",")[0]
            
        else:
            print('None')
        
        return html_url

    def list_url(self,html_url):
        list_html = requests.get(html_url,headers = self.head)
        list_html.encoding = 'utf-8'
        list_player = list_html.text
        play_html = re.findall(r'<p class="play-list">.*?</p>',list_player,re.S)[0]
        info = re.findall(r'<a target="_blank" href="(.*?)">(.*?)</a>',play_html)
        # xunlei_down = re.findall(r'<td class="tit">(.*?)</td>',list_player,re.S)
        # #thunder = re.findall(r'<a href="(.*?)" title="(.*?)" target="_self">.*?</a>',xunlei_down,re.S)
        # print(xunlei_down)
        thunder = re.findall(r'<span id=".*?"><a href="(.*?)" title="(.*?)".*?</span>',list_player,re.S)
        if thunder:
            print("%s迅雷下载地址：%s"%(thunder[0][1],thunder[0][0]))

        print(vod_name + "共%s集"%len(info))
        
        global juji
        while True:
            try:
                juji = input("请输入想要下载的剧集：")
                juji = int(juji)
            except:
                print('你的输入有误')
            else:
                if juji <= len(info) and juji >= 1:
                    break
                else:
                    print('你的输入有误')
            
        player_url = info[0-juji][0]
        
        return player_url

    def down_MP4(self,down_url,vod_name,juji):
        #print("我是mp4函数"+down_url)
        path = "E:\\4k屋\\%s-第%s集.mp4"%(vod_name,juji)
        start = time.time()
        size = 0
        resopnse = requests.get(down_url,stream = True)
        chunk_size = 1024
        content_size = int(resopnse.headers["content-length"])
        
        if resopnse.status_code == 200:
            print("[文件大小]：%0.2f MB,默认下载路径E:\\4k屋"%(content_size / chunk_size / 1024))
            with open(path,"wb") as file:
                for i in resopnse.iter_content(chunk_size=chunk_size):
                    file.write(i)
                    size += len(i)
                    print("\r"+"[下载进度]:%s%.2f%%"%(">"*int(size*50/ content_size),float(size / content_size *100)),end = "")
            end = time.time()
            print("\n"+"《%s》下载完成!用时%.2f秒。\n"%(vod_name,end-start))
        else:
            print("下载失败，请稍后再试！")
        time.sleep(5)  
        Run.main()

    def down_ts(self,datas):
        self.jindu += 1 
        resopnse = requests.get(datas)
        if resopnse.status_code == 200:
            move = resopnse.content
            path = 'E:/4K屋/temp/%s/%s'%(vod_name,juji)
            if not os.path.exists(path):
                os.makedirs(path)
            
            with open('E:/4K屋/temp/%s/%s/%s'%(vod_name,juji,datas.split('/')[-1]),'wb') as f: #ts完整路径进行切片，取最后一个值
                f.write(move)
            
            #print('\r当前速度:{:.2f}%'.format(100/self.file_size*self.jindu),end='')
            aaa = (self.jindu / (self.file_size)) * 20
            s = '\r[当前进度:]{:20}>{:0.2f} %'.format('>'*int(aaa), aaa*5)
            print(s,end='')

    def allok(self):
        try:
            os.system('copy /b E:\\4K屋\\temp\\%s\\%s\\*.ts E:\\4K屋\\%s第%s集.ts'%(vod_name,juji,vod_name,juji)) #调用cmd自带二进制合并文件方式
            os.system('rmdir /s/q E:\\4K屋\\temp')
            print("%s第%s集，下载成功 ~^o^~ 默认下载路径E://4K屋"%(vod_name,juji)) 
            time.sleep(5)

        except:
            print("下载失败，请稍后重试")
          

    def get_tsurl(self,down_url):
        ts_link = requests.get(down_url).text
        #ts_link.strip("\r")
        ts_qianzhui = down_url.replace(down_url.split("/")[-1],"")
        ts_url = ts_link.split("\n")
        
        data = []
        for name in ts_url:
            if ".ts" in name:
                down_ts = ts_qianzhui + name
                data.append(down_ts)
        
        self.file_size = len(data)
        return data



    def get_fileurl(self,list_url):
        player = self.host_url + list_url
        html= requests.get(player)
        html.encoding = "utf-8"
        html = html.text
        playerlink = re.search(r'height="483" src="(.*?)" frameborder="0"',html,re.S)
        print("播放链接：%s"%self.host_url + list_url)
        
        file_url = re.search(r'=http(.*?)(m3u8|mp4)',playerlink.group(),re.S)

        if file_url:
            down_url = file_url.group().strip("=")
            geshi = file_url.group(2)
            if geshi == "mp4":
                self.down_MP4(down_url,vod_name,juji)
            elif geshi == "m3u8":
                m3u8_html = requests.get(down_url).text
                if m3u8_html:
                    m3u8_html1 = m3u8_html.split('\n')
                    if len(m3u8_html1) > 3:
                        pass
                    else:
                        url1 = down_url.strip("index.m3u8")
                        down_url = url1 + m3u8_html1[-1]                
        else:
            print("此链接链接外网，不支持下载！")
            Run.main()
        print(down_url)
        return down_url


    def main(self):
        os.system("cls")
        __version__ = '1.0'
        NAME = '4k屋资源下载'   

        msg = """
            +------------------------------------------------------------+
            |                                                            |
            |                                                            |
            |                 欢迎使用{} V_{}                 |
            |                                                            |
            |                               Copyright (c) 2018 lyjxhxn   |
            +------------------------------------------------------------+
            """.format(NAME, __version__)
        print(msg)  
        name = input("请输入想要下载的电影或电视剧：").strip()
        if name:
            self.jindu = 0
            self.file_size = 0
            html_url = self.get_search(name)
            list_url = self.list_url(html_url)
            down_url = self.get_fileurl(list_url)
            datas = self.get_tsurl(down_url)
            print('正在缓存%s第%s集...'%(vod_name,juji))
            requests = threadpool.makeRequests(self.down_ts,datas) #进程传入任务及完成ts链接
            [pool.putRequest(req) for req in requests] #启用限制进程数
            pool.wait() #等待
            
            #下载完成后执行，linux 没法用
            self.allok() 
        else:
            os.system('cls')
            print('你的输入有误')
        return
           

if __name__ == '__main__':
    Run = Run()
    while True:
        
        Run.main()
   




  