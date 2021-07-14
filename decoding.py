from PIL import Image
import math
import re
import os
from datetime import datetime
# def get_img(img_url):


#需要一个多线程找图片的函数
#需要一个能够防止在多线程情况下出错的本子搜索（就是每次都创建一个新的文件夹，可以通过时间戳）
def pic_decode(img_url,output_file=""):
    """
    该函数对某个文件夹下的图片进行解密并在指定文件夹存储
    """
    source_img=Image.open(img_url)
    w,h=source_img.size
    decode_img=Image.new("RGB",(w,h))
    num=10
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

def decode_all(file_url):
    #下面的代码似乎不是实时的，正好符合要求，因为walk只执行一次。
    temp_file=datetime.now().strftime("%Y%m%d%H%M%S")
    os.makedirs(temp_file)
    for _,_,files in os.walk(file_url):
        for file in files:
            pic_decode(file_url+"/"+file,temp_file)
            
"""
工作步骤梳理：
1.获取指令，创建线程，根据输入变量创建comic。
2.进行网站搜索，获取缩略图以及名字，等待下一指令
3.根据指令选择对应的，得到章节信息并返回，等待下一指令
4.根据章节信息，进行图片处理、打包、发至群中
5.线程结束

具体实现方案，在demo另外进行封装，只将信息传入一个控制流，用来分辨是正常信息还是指令。
一个人在一个时间能使用多个工作类，但是一个工作类只能使用一个
"""
class comic:
    """
    为什么需要这个类呢？
    我们需要得到通过爬虫网站得到其章节信息等，所以这些信息需要进行存储
    还要考虑能否查到、缩略图等因素
    """
    def __init__(self,comic_name,wx_id):
        #name是查询漫画的名字
        #id是查询人，用于对比，对应多处理的情况
        self.comic_name=comic_name
        self.wx_id=wx_id
        self.T=datetime.now().strftime("%Y%m%d%H%M%S")



if __name__=="__main__":
    decode_all("testfile")
    # source_img=Image.open("./00001 (1).jpg")
    # w,h=source_img.size
    # decode_img=Image.new("RGB",(w,h))
    # num=10
    # remainder=h%num
    # copyW=w
    # for i in range(num):
    #     copyH = math.floor(h/num)
    #     py= copyH*i
    #     y=h-(copyH*(i+1))-remainder
    #     if i ==0:
    #         copyH=copyH+remainder
    #     else:
    #         py=py+remainder
    #     temp_img=source_img.crop((0,y,copyW,y+copyH))
    #     decode_img.paste(temp_img,(0,py,copyW,py+copyH))
    #     #decode_img[0,copyW][py:py+copyH]=source_img[0:copyW][y:y+copyH]
    # decode_img.save("./decode.jpg")