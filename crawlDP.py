#-*-coding:utf-8-*-
import requests
import re
import time
import lxml
import lxml.html
import socket
etree=lxml.html.etree
import threading

headers = {
    "Host": "www.dianping.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Cookie":"_lxsdk_cuid=16a06db6644c8-0c8e4b9330017d-594d2a16-144000-16a06db6645c8; _lxsdk=16a06db6644c8-0c8e4b9330017d-594d2a16-144000-16a06db6645c8; _hc.v=bd66d284-6d44-578d-784e-b36dc0f8d48f.1554893204; s_ViewType=10; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; dper=744b6a929fe6a4d7fda39a1e86972c290074f0bd9b32b9b235444dea8b0d6aea441f6877e07f74b6c14a745ef4231defb368b1f63e59b265948047f473c06beb8151eab1a8493f174f8156888f65d5b2c48d40c53df57a1cfb1a3cf93c84073b; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_0589943746; ctu=ed17454160c744579d75b043e7e805bc0064f703b19daf393e3744cfde82108e; uamo=15629073250; cy=70; cye=changchun; _lxsdk_s=16a47b8a52a-a6a-69-892%7C1267954787%7C18"
}

headers_loc={
    "Host": "api.map.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Chookie":"8f.1554893204; s_ViewType=10; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; dper=744b6a929fe6a4d7fda39a1e86972c290074f0bd9b32b9b235444dea8b0d6aea441f6877e07f74b6c14a745ef4231defb368b1f63e59b265948047f473c06beb8151eab1a8493f174f8156888f65d5b2c48d40c53df57a1cfb1a3cf93c84073b; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_0589943746; ctu=ed17454160c744579d75b043e7e805bc0064f703b19daf393e3744cfde82108e; uamo=15629073250; cy=2; cye=beijing; _lxsdk_s=16a4527191a-628-cda-7eb%7C1267954787%7C43"
}


proxy = {
    'http': '116.28.50.142:80',
    'https': '116.28.50.142:80',
}
'''
    "beijing","shanghai","tianjin","chongqing",
    
    
    "haerbin","changchun","shenyang","huhehaote",
    "shijiazhuang","wulumuqi","lanzhou","xining","xian","yinchuan","zhengzhou","jinan","taiyuan",
    "hefei","wuhan","changsha","nanjing","chengdu","guiyang","kunming","nanning","lasa",
    "hangzhou","nanchang","guangzhou","fuzhou"
'''
cities = [
    "beijing", "shanghai", "tianjin", "chongqing",
    "haerbin", "changchun", "shenyang", "huhehaote",
    "shijiazhuang", "wulumuqi", "lanzhou", "xining", "xian", "yinchuan", "zhengzhou", "jinan", "taiyuan",
    "hefei", "wuhan", "changsha", "nanjing", "chengdu", "guiyang", "kunming", "nanning", "lasa",
    "hangzhou", "nanchang", "guangzhou", "fuzhou",
    "shanghai","kunming"
]

# 设置socket层的超时时间
socket.setdefaulttimeout(200)



Pinyin2Characters={
    "beijing":"北京",
    "shanghai":"上海",
    "tianjin":"天津",
    "chongqing":"重庆",
    "haerbin":"哈尔滨",
    "changchun":"长春",
    "shenyang":"沈阳",
    "huhehaote":"呼和浩特",
    "shijiazhuang":"石家庄",
    "wulumuqi":"乌鲁木齐",
    "lanzhou":"兰州",
    "xining":"西宁",
    "xian":"西安",
    "yinchuan":"银川",
    "zhengzhou":"郑州",
    "jinan":"济南",
    "taiyuan":"太原",
    "hefei":"合肥",
    "wuhan":"武汉",
    "changsha":"长沙",
    "nanjing":"南京",
    "chengdu":"成都",
    "guiyang":"贵阳",
    "kunming":"昆明",
    "nanning":"南宁",
    "lasa":"拉萨",
    "hangzhou":"杭州",
    "nanchang":"南昌",
    "guangzhou":"广州",
    "fuzhou":"福州"

}




#获取城市对应的url分类
def GetClass(city_url):
    FoodClassDict = dict()
    # url = "http://www.dianping.com/wuhan/ch10/g112p1"

    data = requests.get(city_url, headers=headers, timeout=500).text
    f = etree.HTML(data)
    FoodClassList = f.xpath('//*[@id="classfy"]/a')
    for FoodClass in FoodClassList:
        ClassURL = FoodClass.xpath('./@href')
        ClassName = FoodClass.xpath('./span/text()')[0]
        FoodClassDict["{}".format(ClassName)] = ClassURL
    return FoodClassDict
    pass
'''
//*[@id="shop-all-list"]/ul/li[1]/div[2]/span/span[1]/b/svgmtsi[1]
//*[@id="shop-all-list"]/ul/li[1]/div[2]/span/span[1]/b/svgmtsi[2]
'''

def GetLoc(url_loc):
    # time.sleep(1)
    jsondata = requests.get(url_loc, headers=headers_loc, timeout=5000).json()

    if jsondata['result']:
        # print("1")
        lng = jsondata['result']['location']['lng']
        lat = jsondata['result']['location']['lat']
        # print(lng, lat)
    else:
        lng = 0
        lat = 0

    return lng,lat

'''
//*[@id="shop-all-list"]/ul/li[2]/div[2]/span/span[1]/b/svgmtsi[1]
'''

def GetDP(base_url,ScoreList):

    #遍历各个城市
    for city in cities:
        city_url=base_url.replace("wuhan",city,1)

        # 存放不同城市美食分类url的字典
        FoodClassDict=GetClass(city_url)

        # 将拼音转化为汉字
        # city_Charac=Pinyin2Characters[city]

        with open("./output/data/{}.tsv".format(city),"w",encoding="utf-8") as f_food:
            id=0
            for key in FoodClassDict:
                No=0
                url_class=FoodClassDict[key]

                #获取这一分类页数
                data = requests.get(url_class[0], headers=headers, timeout=5000).text
                f = etree.HTML(data)

                # 倒数第一为“下数一页”，倒第二位最后一页
                pages_list=f.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/a/@title')
                if len(pages_list):
                    pages=pages_list[-2]
                else:
                    pages=1

                #遍历分类中所有页数的所有食物
                for i in range(int(pages)):

                    url = url_class[0]+ "o3"+"p{}".format(i+1)

                    # 根据页数不同更换url
                    data = requests.get(url, headers=headers, timeout=5000).text
                    f = etree.HTML(data)

                    Shops = f.xpath('//*[@id="shop-all-list"]/ul/li')

                    for shop in Shops:

                        id+=1
                        print(id,end="\t")
                        f_food.write(str(id)+"\t")

                        No += 1
                        print(No, end="\t")
                        f_food.write(str(No)+"\t")

                        #获取店铺名
                        shopname=shop.xpath('./div[2]/div[1]/a[1]/h4/text()')
                        print(shopname[0], end="\t")
                        f_food.write(shopname[0] + "\t")


                        # # 获取地址
                        # address=shopname[0]
                        # url_loc = "http://api.map.baidu.com/geocoder?" \
                        #       "address={}" \
                        #       "&output=json" \
                        #       "&key=0ckDZzMqEDcKxSaCeMVnIH9OVVOoKvd7" \
                        #       "&city={}".format(address, city_Charac)
                        #
                        # lng, lat=GetLoc(url_loc)
                        # print(lng, lat, end="")
                        # f_food.write(str(lng) + "\t")
                        # f_food.write(str(lat) + "\t")

                        #菜系
                        print(key,end="\t")
                        f_food.write(key + "\t")


                        # 获取评论数
                        comment_num=''
                        comments = shop.xpath('./div[2]/div[2]/a[1]')
                        for comment in comments:
                            t = comment.xpath('./b/text()')
                            c = comment.xpath('./b/svgmtsi/text()')
                        if len(t):
                            comment_num = '-1'
                        elif len(c):
                            for j in range(len(c)):
                                comment_num += ScoreList[c[j]]
                        else:
                            comment_num = '-1'

                        print(comment_num, end="\t")
                        f_food.write(comment_num + "\t")


                        #获取评分
                        scores = shop.xpath('./div[2]/span/span')
                        for score in scores:
                            num=0.0
                            t = score.xpath('./b/text()')
                            c = score.xpath('./b/svgmtsi/text()')
                            if t[0] == ".":
                                num = ScoreList[c[0]] + '.' + ScoreList[c[1]]#Unicode2NUM   ScoreList
                            else:
                                num = ScoreList[c[0]] + '.1'#Unicode2NUM



                            print(num,end="\t")
                            f_food.write(num+"\t")

                        #获取推荐菜
                        recommendations=shop.xpath('./div[2]/div[4]/a')
                        for recommendation in recommendations:
                            dish_name=recommendation.xpath('./text()')
                            if len(dish_name):
                                print(dish_name[0],end="\t")
                                f_food.write(dish_name[0]+"\t")
                        print()
                        f_food.write("\n")
                time.sleep(10)
            time.sleep(10)
        time.sleep(10)
        f_food.close()
        id=0


#读取css的url，将svg转化为数字
def SVG2NUM():
    url="http://www.dianping.com/wuhan/ch10/g113"
    data = requests.get(url, headers=headers, timeout=5000).text
    # f = etree.HTML(data)
    # print(data)
    css_url = "http:" + re.search('(//.+svgtextcss.+\.css)', data).group()
    css_res = requests.get(css_url)
    # 这一步得到的列表内容为css中class的名字及其对应的偏移量
    css_list = re.findall('(wv\w+){background:(.+)px (.+)px;', '\n'.join(css_res.text.split('}')))
    # 过滤掉匹配错误的内容，并对y方向上的偏移量初步处理
    css_list = [[i[0], i[1], abs(float(i[2]))] for i in css_list if len(i[0]) == 5]
    # y_list表示在y方向上的偏移量，完成排序和去重
    y_list = [i[2] for i in css_list]
    y_list = sorted(list(set(y_list)))
    # 生成一个字典
    y_dict = {y_list[i]: i for i in range(len(y_list))}
    # 提取svg图片的url
    svg_url = "http:" + re.findall('class\^="wv".+(//.+svgtextcss.+\.svg)', '\n'.join(css_res.text.split('}')))[0]
    svg_res = requests.get(svg_url)
    # 得到svg图片中的所有数字
    digits_list = re.findall('>(\d+)<', svg_res.text)

    ScoreList=dict()
    for i in css_list:
        # index表示x方向上的索引(最小的索引值是0)
        index = int((float(i[1]) + 7) / -12)
        ScoreList[i[0]] = digits_list[y_dict[i[2]]][index]
    # print(temp)
    return ScoreList


# 该函数仅爬取单一城市对应url的数据
def GetDPThreading(city):
    print("The {} is starting: ".format(city),end="")
    print(time.asctime(time.localtime(time.time())))

    base_url = "http://www.dianping.com/wuhan/ch10"
    #遍历各个城市
    # for city in cities:
    city_url=base_url.replace("wuhan",city,1)

    # 存放不同城市美食分类url的字典
    FoodClassDict=GetClass(city_url)

    with open("./output/data/{}.tsv".format(city),"w",encoding="utf-8") as f_food:
        id=0
        for key in FoodClassDict:
            No=0
            url_class=FoodClassDict[key]

            #获取这一分类页数
            data = requests.get(url_class[0], headers=headers, timeout=5000).text
            f = etree.HTML(data)

            # 倒数第一为“下数一页”，倒第二位最后一页
            pages_list=f.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/a/@title')
            if len(pages_list):
                pages=pages_list[-2]
            else:
                pages=1

            #遍历分类中所有页数的所有食物
            for i in range(int(pages)):

                url = url_class[0]+ "o3"+"p{}".format(i+1)

                # 根据页数不同更换url
                data = requests.get(url, headers=headers, timeout=5000).text
                f = etree.HTML(data)

                Shops = f.xpath('//*[@id="shop-all-list"]/ul/li')

                for shop in Shops:

                    id+=1
                    # print(id,end="\t")
                    f_food.write(str(id)+"\t")

                    No += 1
                    # print(No, end="\t")
                    f_food.write(str(No)+"\t")

                    #获取店铺名
                    shopname=shop.xpath('./div[2]/div[1]/a[1]/h4/text()')
                    # print(shopname[0], end="\t")
                    f_food.write(shopname[0] + "\t")


                    #菜系
                    # print(key,end="\t")
                    f_food.write(key + "\t")


                    # 获取评论数
                    comment_num=''
                    comments = shop.xpath('./div[2]/div[2]/a[1]')
                    for comment in comments:
                        t = comment.xpath('./b/text()')
                        c = comment.xpath('./b/svgmtsi/text()')
                    if len(t):
                        comment_num = '-1'
                    elif len(c):
                        for j in range(len(c)):
                            comment_num += ScoreList[c[j]]
                    else:
                        comment_num = '-1'
                    # print(comment_num, end="\t")
                    f_food.write(comment_num + "\t")

                    #获取评分
                    scores = shop.xpath('./div[2]/span/span')
                    for score in scores:
                        num=0.0
                        t = score.xpath('./b/text()')
                        c = score.xpath('./b/svgmtsi/text()')
                        if t[0] == ".":
                            num = ScoreList[c[0]] + '.' + ScoreList[c[1]]#Unicode2NUM   ScoreList
                        else:
                            num = ScoreList[c[0]] + '.1'#Unicode2NUM
                        # print(num,end="\t")
                        f_food.write(num+"\t")

                    #获取推荐菜
                    recommendations=shop.xpath('./div[2]/div[4]/a')
                    for recommendation in recommendations:
                        dish_name=recommendation.xpath('./text()')
                        if len(dish_name):
                            # print(dish_name[0],end="\t")
                            f_food.write(dish_name[0]+"\t")
                    # print()
                    f_food.write("\n")
            time.sleep(10)
        time.sleep(10)
    f_food.close()
    print("The {} is finish: ".format(city), end="")
    print(time.asctime(time.localtime(time.time())))


def Slice(Threadnum):
    cities_list = []
    clen=len(cities)

    for i in range(0,clen,Threadnum):
        if i+Threadnum<clen:
            temp = cities[i:i + Threadnum]
            cities_list.append(temp)
        else:
            temp = cities[i:]
            cities_list.append(temp)



    # deta=int(clen/Threadnum)
    #
    #
    # for i in range(0,clen,deta):
    #     temp=cities[i:i+deta]
    #     cities_list.append(temp)
    # return cities_list

# 利用threading进行分布式爬取
# 默认为8线程
def Distributed(Threadnum=8):
    threads=[]

    cities_list=Slice(Threadnum)

    for city_list in cities_list:
        for city in city_list:
            t=threading.Thread(target=GetDPThreading,args=(city,))
            threads.append(t)
        for t in threads:
            t.setDaemon(True)
            t.start()
        t.join()
        threads.clear()
    pass



if __name__ == '__main__':


    Unicode2NUM = {
        '\uee53': '0',
        '\ue3a3': '2',
        '\uf759': '3',
        '\uf831': '4',
        '\ue2ba': '5',
        '\ue96b': '6',
        '\ue7d4': '7',
        '\uf8d6': '8',
        '\ueb25': '9'
    }  # class-digit字典


    #基础url
    base_url = "http://www.dianping.com/wuhan/ch10"
    #获取SVG对应的评分列表
    ScoreList=Unicode2NUM
    # ScoreList=[]
    # 爬取数据
    # GetDP(base_url,ScoreList)


    # 以下为分布式爬取

    Distributed()


    # for i in range(0,30,8):
    #     print(i,end="\t")


    # print(type(cities))
    # GetDPThreading("beijing")

    print("Function Finish.")