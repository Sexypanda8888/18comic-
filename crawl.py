import requests
import threading
import re
import os
import time
import zipfile
import shutil
import math
import hashlib
from PIL import Image
from pic_ops import image_join
class MyThread(threading.Thread):
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

  
    def run(self):
        self.result = self.func(*self.args)
    
    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


def save_img(nurl,output):
    #count需要使用列表，因为是弱复制
    try:
        r=requests.get(nurl,timeout=10)
        content=r.content
    except:
        try:
            r=requests.get(nurl,timeout=10)
            content=r.content
        except:
            #这里要给错误图
            with open("烂掉的图",'rb') as f:
                content=f.read()
                return 0
    
    with open(output,'wb') as f:
        f.write(content)
    return 1

def get_benzi_list(name,fileaddress):
    """
    name:str
    fileaddress:str
    进行搜索的函数，输入需要搜索本子的名称和文件夹地址
    搜索到结果时，至多返回三个结果的链接以及缩略图本地地址
    如果搜索失败，则抛出异常
    如果搜索没有结果，输出两个都是空列表
    """
    url="https://18comic.org/search/photos?search_query="+name
    #url2="https://18comic.org/search/photos?search_query=触电"
    r=requests.get(url)
    #如果直接请求失败了，就要
    if r.status_code!=200:
        raise Exception("请求失败，可能是因为网络问题或者网站改版所导致")
    try:
        link_pattern='list-col.*?\n.*?\n<a href="(.*?)">'#.*?不能匹配换行符，要自己加上
        temp=re.findall(link_pattern,r.text)  #第一次使用findall，可以直接返回一个（）内的列表
        #如果没有检索结果，就返回一个空表
        #如果有检索结果，就创建缩略图并且返回链接和图片url
        links=[]
        img_nurl=[]
        if len(temp)==0:
            raise Exception("没有搜索结果")
        for i in range(len(temp)):
            if i >=3:
                break
            links.append("https://18comic.org"+temp[i])
        img_pattern='data-original="(.*?)"'
        num=len(temp)
        temp=re.findall(img_pattern,r.text)

        for i in range(num):
            if i >=3:
                break
            img_nurl.append(temp[i])

        if not os.path.exists('./'+fileaddress):
            os.makedirs(fileaddress)
        #获取缩略图的过程建议使用多线程
        t=[]
        img_url=[]
        
        for i in range(len(img_nurl)):
            img_url.append("./"+fileaddress+"/benzi_{}.jpg".format(i))
            t.append(MyThread(func=save_img,args=[img_nurl[i],img_url[i]]))
        for i in t:
            i.start()
        for i in t:
            i.join()
        #返回图片url以及链接
    except:
        pass

    return [links,img_url]


def show_episode(url):
    """
    该函数输入选择章节页面的url,输出所有章节形成的列表
    """
    pattern='<a href="(.*?)">\n<li class=".*">'
    r=requests.get(url)
    episode_url=[]
    try:
        temp=re.findall(pattern,r.text)
        if len(temp)==0:
            raise Exception("单章")
        for i in range(len(temp)//2):
            episode_url.append("https://18comic.org"+temp[i])
    except:
        pattern='col btn btn-primary dropdown-toggle reading" href="(.*?)"'
        temp=re.findall(pattern,r.text)
        episode_url.append("https://18comic.org"+temp[0])
    return episode_url

def save_one_episode(url,str_num,fileaddress):
    """
    输入该章的url以及章数以及文件名字，用来创建对应的章节文件
    """
    str_num=str(int(str_num)+1)
    if not os.path.exists(fileaddress):
        os.makedirs(fileaddress)
    episodeadd=fileaddress+"/"+str_num
    #<img src="https://cdn-msp.18comic.org/media/albums/blank.jpg" data-original="https://cdn-msp.18comic.org/media/photos/255011/00050.jpg" id="album_photo_" id="album_photo_00050.jpg
    if not os.path.exists(episodeadd):
        os.makedirs(episodeadd)
    r=requests.get(url)
    pattern='scramble_id = (.*?);\n.*?\n.*?var aid = (.*?);'
    temp=re.search(pattern,r.text)
    scramble_id=temp.group(1)
    aid=temp.group(2)
    pattern='data-original="(.*?)" id="album_photo_(.+?)"'
    temp=re.findall(pattern,r.text)
    img_url=[]
    t=[]
    for i in range(len(temp)):
        img_url.append(fileaddress+"/"+str_num+"/"+temp[i][1])
        t.append(MyThread(func=save_img,args=[temp[i][0],img_url[i]]))
    for i in t:
        i.start()
    for i in t:
        i.join()
    fail=[]
    for i in range(len(t)):
        if t[i].get_result()==0:
            fail.append(i)
    return [img_url,aid,fail] #两者一一对应，后面要拿出来给后面的解密函数使用



def get_content(episode_url:list,st:int,ed:int,fileaddress:str):
    """
    从st开始到ed结束的章节里面
    输入的是集数的list
    st,ed应该为int的，这里数据类型比较繁杂
    返回所有已经获得图片的url以及是否需要进行解密的判断
    """
    t=[]
    for i in range(st-1,ed):
        t.append(MyThread(func=save_one_episode,args=[episode_url[i],str(i),fileaddress]))
    for i in t:
        time.sleep(2)
        i.start()
    for i in t:
        i.join()
    img_data=[]
    for i in t:
        img_data.append(i.get_result())
    return img_data
    #应该要获得所有的url情况以及
    #<img src="https://cdn-msp.18comic.org/media/albums/blank.jpg" data-original="https://cdn-msp.18comic.org/media/photos/255011/00050.jpg
    
    

def check(pattern,text):
    if re.findall(pattern,text)==[]:
        return False
    else:
        return True



def comic_decode(img_url,output_file="",num=0):
    """
    该函数对某个文件夹下的图片进行解密并在指定文件夹存储
    """
    if num==0:
        return img_url
    source_img=Image.open(img_url)
    w,h=source_img.size
    decode_img=Image.new("RGB",(w,h))
    remainder=h%num
    copyW=w
    for i in range(num):
        copyH = math.floor(h/num)
        py= copyH*i
        y=h-(copyH*(i+1))-remainder
        if i ==0:
            copyH=copyH+remainder
        else:
            py=py+remainder
        temp_img=source_img.crop((0,y,copyW,y+copyH))
        decode_img.paste(temp_img,(0,py,copyW,py+copyH))
        #decode_img[0,copyW][py:py+copyH]=source_img[0:copyW][y:y+copyH]
    pattern="(.*?)/(.*?).jpg"
    match=re.search(pattern,img_url)
    if output_file!="":
        save_url=output_file+"/"+match.group(2)+"_d.jpg"
    else:
        save_url=match.group(1)+"/"+match.group(2)+"_d.jpg"
    decode_img.save(save_url)
    return save_url

def get_num(aid,img_url):
    '''
    获取分割数量的函数
    '''
    #220980
    #268850
    pattern='/([0-9]*)\.jpg'
    l=re.findall(pattern,img_url)[0]
    num=0
    if aid<220980:
        num=0
    elif aid<268850:
        num=10
    else:
        string=str(aid)+l
        string=string.encode()
        string=hashlib.md5(string).hexdigest()
        num=ord(string[-1])
        num%=10
        num=num*2+2
    return num


class Search_benzi:
    def __init__(self):
        self.name=''  #本子名称
        self.fileaddress=str(int(time.time()))
        self.has_reached_episodelist=False
        self.has_complited=False
        self.choice=""
        self.st=None
        self.ed=None
            
    def __del__(self):
        shutil.rmtree(self.fileaddress)
        print("搜本服务结束")
    def get_name(self):
        self.name=input('请输入对应的本子名:\n')
    
    def search_results(self):
        self.benzi_link,self.thumb_url=get_benzi_list(self.name,self.fileaddress)
        #如果两个是空列表，说明没有搜索成功
        if self.benzi_link==[] or self.thumb_url == []:
            print("没有找到对应的搜索结果呢")
            return False
        else:
            #进行缩略图处理
            temp_url=self.fileaddress+"/temp.jpg"
            if len(self.thumb_url)==1:
                temp_url=self.thumb_url[0]
            elif len(self.thumb_url)>=2:
                image_join(self.thumb_url[0],self.thumb_url[1],temp_url,flag="vertical")
                if len(self.thumb_url)==3:
                    image_join(temp_url,self.thumb_url[2],temp_url,flag="vertical")
            print('找到%d个搜索结果，请根据缩略图选择1~%d编号:'%(len(self.benzi_link),len(self.benzi_link)))
            return True


    def choose_benzi(self):
        #要求为单个数字，是否为str另说，需要进行合法性检查。
        #在合法性这里犯难了。不知道该怎么办，因为我要不合法就发送信息后直接继续挂起。
        #每次唤醒之后进行检查+赋值
        #检查的是所有的！
        pattern="([1-{}])".format(len(self.benzi_link))
        m=re.findall(pattern,input(''))
        if m==[]:
            print('输入的格式对不上，对不上\n或者是选了不存在的选项')
            return False
        else:
            self.choice=m[0]
            print("明白，请稍等...")
            return True


    def show_episode(self):
        try:
            self.episode_url=show_episode(self.benzi_link[int(self.choice)-1])
            self.benzi_name=self.benzi_link[int(self.choice)-1].split('/')[-1]
            if len(self.episode_url)>1:
                print('该作品总共有%d章节:\n请按格式"a b"(1<=a<=b<=%d)选择你需要的'%(len(self.episode_url),len(self.episode_url)))
            elif len(self.episode_url)==1:
                print('单本作品，无需选择章节数,正在下载:')
                self.st=1
                self.ed=1
            return True
        except:
            print('发生了网络波动之类的错误，请重新输入选择数字')
            return False
    def choose_episode(self):
        pattern="(\d+) +(\d+)"
        m=re.findall(pattern,input(''))
        if m==[]:
            #有的反应比较快的，就不需要@
            print('输入的格式对不上，对不上。请重试')

            return False
        self.st=int(m[0][0])
        self.ed=int(m[0][1])
        if self.st>self.ed:
            self.st,self.ed=self.ed,self.st
        if self.ed>len(self.episode_url):

            print('超出了章节范围，请重试')
            
            return False
        print('正在下载...')
        return True
    def get_content(self):
        self.imagedata=get_content(self.episode_url,self.st,self.ed,self.fileaddress)
        for i in self.imagedata:
            #i:[每个图片的url],判断要不要进行解密,[加载失败的图片位置]
            #这里使用获得分割数量的函数

            temp=[]
            for j in i[0]:
                num=get_num(int(i[1]),j)
                temp.append(comic_decode(j,num=num))
            i[0]=temp
        zip_name=self.benzi_name+".zip"
        zip_file = zipfile.ZipFile(zip_name,'w')
        for i in self.imagedata:
            for j in i[0]:
                temp=j.split("/")
                arcname=temp[-2]+"/"+temp[-1]
                zip_file.write(filename=j,arcname=arcname)
        zip_file.close()
        #同时为了方便debug以及能做到个人，将其做成下列形式
            #后面是发送文件
#下面正式开始线程操作

if __name__=="__main__":
    benzi_obj=Search_benzi()
    benzi_obj.get_name()
    if not benzi_obj.search_results():
        exit()
    while not benzi_obj.choose_benzi():
        pass
    while not benzi_obj.show_episode():
        pass
    if len(benzi_obj.episode_url)>1:
        #假如有章节
            while not benzi_obj.choose_episode():
                pass
            benzi_obj.get_content()
    else:
        #假如是单章
        benzi_obj.get_content()
    
    # sh=input("请输入你需要搜索的名称：\n")
    # T=time.time()
    # fileaddress=str(int(T))
    # benzi_link,thumb_url=get_benzi_list(sh,fileaddress)
    # print("搜索到{}个结果，其缩略图分别为：\n".format(len(benzi_link)))
    # for i in thumb_url:
    #     print(i)
    # select=input("请输入对应数字选择本子:\n")
    # episode_url=show_episode(benzi_link[int(select)-1])
    # print("该作品总共有{}章节".format(len(episode_url))) #如果只有一个章节那么就应该直接下载
    # st=input("请输入起始章节:")
    # ed=input("请输入结尾章节:")
    # imagedata=get_content(episode_url,int(st),int(ed),fileaddress)
    # for i in imagedata:
    #     #i:[每个图片的url],判断要不要进行解密,[加载失败的图片位置]
    #     if i[1]==True:
    #         temp=[]
    #         for j in i[0]:
    #             temp.append(pic_decode(j))
    #         i[0]=temp
    #     else:
    #         pass
    
    # episode_url=show_episode("https://18comic.org/album/112952/1ldk-jk-%E7%AA%81%E7%84%B6%E5%90%8C%E5%B1%85-%E7%B7%8A%E8%B2%BC-%E5%88%9D%E6%AC%A1h-%E4%BA%8C%E4%B8%89%E6%9C%88%E3%81%9D%E3%81%86-1ldk-jk-%E3%81%84%E3%81%8D%E3%81%AA%E3%82%8A%E5%90%8C%E5%B1%85-%E5%AF%86%E8%91%97-%E5%88%9D%E3%82%A8%E3%83%83%E3%83%81-%E7%A6%81%E6%BC%AB%E6%BC%A2%E5%8C%96%E7%B5%84-%E5%A4%A2%E4%B9%8B%E8%A1%8C%E8%B9%A4%E6%BC%A2%E5%8C%96%E7%B5%84")
    # print(episode_url)
    # get_content(episode_url,1,3,str(int(time.time())))
    # a=show_episode("https://18comic.org/album/178177/%E7%A6%81%E6%BC%AB%E6%BC%A2%E5%8C%96%E7%B5%84-%E9%BB%91%E7%B5%B2%E5%A6%B9%E6%91%B8%E6%91%B8%E8%A2%AB%E6%8A%93%E5%88%B0-kidmo-january-2020-part-2")
    # print(a)
"""
<img src="https://cdn-msp.18comic.org/media/photos/264883/00001.jpg?v=1625907433" data-original="https://cdn-msp.18comic.org/media/photos/264883/00001.jpg?v=1625907433" id="album_photo_00001.jpg" class="lazy_img img-responsive-mw" style="min-height: 200px; display: inline; background-image: url(&quot;https://cdn-msp.18comic.org/media/photos/264883/00001.jpg?v=1625907433&quot;);" data-page="0">
<img src="https://cdn-msp.18comic.org/media/photos/181852/00001.jpg?v=1593867290" data-original="https://cdn-msp.18comic.org/media/photos/181852/00001.jpg?v=1593867290" id="album_photo_00001.jpg" class="lazy_img img-responsive-mw" style="min-height: 200px; display: inline; background-image: url(&quot;https://cdn-msp.18comic.org/media/photos/181852/00001.jpg?v=1593867290&quot;);" data-page="0">
"""