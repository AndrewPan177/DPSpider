#-*-coding:utf-8-*-
import requests
import json
import time
import sys
import os
import os.path
import csv
import psycopg2
import re

# 读写tsv
csv.register_dialect('mydialect',delimiter='\t',quoting=csv.QUOTE_ALL)

# 防止数据量过大
maxInt = sys.maxsize
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

'''

http://api.map.baidu.com/geocoder?address=妈妈菜馆&output=json&key=0ckDZzMqEDcKxSaCeMVnIH9OVVOoKvd7&city=武汉

'''

Pinyin2Characters = {
    "beijing": "北京",
    "shanghai": "上海",
    "tianjin": "天津",
    "chongqing": "重庆",
    "haerbin": "哈尔滨",
    "changchun": "长春",
    "shenyang": "沈阳",
    "huhehaote": "呼和浩特",
    "shijiazhuang": "石家庄",
    "wulumuqi": "乌鲁木齐",
    "lanzhou": "兰州",
    "xining": "西宁",
    "xian": "西安",
    "yinchuan": "银川",
    "zhengzhou": "郑州",
    "jinan": "济南",
    "taiyuan": "太原",
    "hefei": "合肥",
    "wuhan": "武汉",
    "changsha": "长沙",
    "nanjing": "南京",
    "chengdu": "成都",
    "guiyang": "贵阳",
    "kunming": "昆明",
    "nanning": "南宁",
    "lasa": "拉萨",
    "hangzhou": "杭州",
    "nanchang": "南昌",
    "guangzhou": "广州",
    "fuzhou": "福州",
    "haikou":"海口"
}

headers_loc = {
    "Host": "api.map.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Chookie": "BAIDUID=52FC69A7130A659CADFA949A2888FCAB:FG=1; BIDUPSID=52FC69A7130A659CADFA949A2888FCAB; PSTM=1541585314;"
               " MCITY=-218%3A; BDUSS=nBwNGVQVWF6TE9NflFESW9XdzYzN1hyS1ZucHRVTW1XVVNYTTloYVJNS2gzdEpjRVFBQUFBJCQAAAAAAAAAA"
               "AEAAAC4uZSFsru8-7DXybPNoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKFRq1yhUatcN; "
               "delPer=0; PSINO=1; ZD_ENTRY=bing; pgv_pvi=5365540864; pgv_si=s9623355392; "
               "H_PS_PSSID=1451_28777_21120_28775_28722_28836_28584_26350_28604_22157; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0"
}

proxy = {
    'http': '116.28.50.142:80',
    'https': '116.28.50.142:80',
}

ak = "0ckDZzMqEDcKxSaCeMVnIH9OVVOoKvd7"


'''
重复值：4598
缺失值 6581
缺失值 18440
在19666处可能会有重复值
'''


def GetLoc(filenameList):
    for filename in filenameList:

        firstname, lastname = filename.split(".")
        cityname, mode = firstname.split("_")
        # url="http://api.map.baidu.com/geocoder?address=妈妈菜馆&output=json&key=0ckDZzMqEDcKxSaCeMVnIH9OVVOoKvd7&city=武汉"
        # data=requests.get(url).json()
        count = 0
        with open("./output/final/data/{}.tsv".format(firstname), "r", encoding="utf8")as f_in,\
                open("./output/final/loc/{}_loc.tsv".format(cityname), "a", encoding="utf-8") as f_out:
            file_list = csv.reader(f_in, 'mydialect')

            for lines in file_list:
                count += 1
                if count > 20661 and count<20663:
                    # time.sleep(0.5)
                    # print(lines[2])
                    address = lines[2]
                    city = Pinyin2Characters[cityname]
                    # print(address,city)

                    url = "http://api.map.baidu.com/geocoder?" \
                        "address={}" \
                        "&output=json" \
                        "&key=0ckDZzMqEDcKxSaCeMVnIH9OVVOoKvd7" \
                        "&city={}".format(address, city)

                    data = requests.get(url, headers=headers_loc, timeout=50000).json()
                    # print(type(data['result']['location']['lng']))
                    # lng=0;lat=0

                    if len(data["result"]):
                        # print("1")
                        lng = data['result']['location']['lng']
                        lat = data['result']['location']['lat']
                        # print(lng, lat)
                    else:
                        lng = 0
                        lat = 0
                        pass
                    i = 0
                    for item in lines:
                        i += 1
                        f_out.write(item+"\t")
                        print(item, end="\t")

                        if i == 3:
                            print(lng, lat, end="\t")
                            f_out.write(str(lng) + "\t")
                            f_out.write(str(lat) + "\t")

                        else:
                            pass

                    print()
                    f_out.write("\n")

            # lng=data['result']['location']['lng']
            # lat=data['result']['location']['lat']
            # print(lng,lat)


def GetFile(rootdir):

    filenameList = []
    for parent, dirnames, filenames in os.walk(rootdir):  # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:
            filenameList.append(filename)
    # print(filenameList)
    return filenameList
    pass

'''
1276-1544   3061-3119  3001-3408
268  59  327
'''


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


# t为第二次骚动的地方
def RecList(line,t):
    # 获取列表除空字符外的实际长度
    tag=0
    i=0
    recomment0=[]
    temp=line[t:]
    for e in range(len(temp)):
        if temp[e] and e<3:
            tag+=1
    if tag==3:
        recomment0=line[t:t+3]
    elif tag<3:
        recomment0=line[t:t+tag]
    return recomment0


# 处理带有坐标的数据，将缺失的评分值补全
# 将推荐菜后多余的空字符清除
def Write(line):

    # 骚动开始的地方
    # 无坐标则为5，有则为7
    begin=5


    id=[]
    No=[]
    Shopname=[]
    Lng=[]
    Lat=[]
    type=[]
    comments=[]
    scores=[]
    recomment=[]

    id.append(int(line[0]))
    No.append(int(line[1]))
    Shopname.append(line[2])
    # Lng.append(float(line[3]))
    # Lat.append(float(line[4]))
    type.append(line[3])
    comments.append(int(line[4]))

    lenght=len(line)
    if lenght>begin and line[begin]:
        if line[begin] and is_number(line[begin])==True:
            #表明这里是数字
            for e in line[begin:begin+3]:
                scores.append(float(e))
                recomment=RecList(line,begin+3)
                # recomment=line[begin+3:]
        elif line[begin] and is_number(line[begin])==False:
            #表明这里是非数字（推荐菜）
            scores=[0.0,0.0,0.0]
            recomment = RecList(line, begin)
            # recomment=line[begin:]
    else:
        scores = [0.0, 0.0, 0.0]

    line_output = id + No + Shopname + type + comments + scores #+ recomment
    # line_output=id+No+Shopname+Lng+Lat+type+comments+scores+recomment


    return line_output




# 修正序号间断问题
# 修正“推荐菜3”后的多余字符问题

def Modify(fileList):

    for filename in fileList:
        firstname,lastname=filename.split(".")
        # print(firstname)


        with open("./output/final/{}.tsv".format(firstname),"r",encoding="utf-8")as f_in,\
                open("./output/test/{}.tsv".format(firstname),"w",encoding="utf-8")as f_out:
            file_list = csv.reader(f_in, 'mydialect')
            for line in file_list:

                line_2=Write(line)

                for item in line_2:
                    # print(item,end="\t")
                    f_out.write(str(item)+"\t")
                f_out.write("\n")

        print("{} is finish.".format(firstname))


    pass

# 验证推荐菜无不可见字符
def Verify(FileList):
    for filename in FileList:
        firstname,lastname=filename.split(".")

        with open("./output/final/{}.tsv".format(firstname), "r", encoding="utf-8")as f_in:
            file_list = csv.reader(f_in, 'mydialect')
            for line in file_list:
                tag=0
                for e in line:
                    if e:
                        tag+=1
                if tag>11:
                    print("{}'s {} is wrong.".format(firstname,line[0]))
                if is_number(line[1])!=True:
                    print("{}'s {} is wrong.".format(firstname, line[0]))
        print("{} is finish.".format(firstname))




# 随便读一下csv
def ReadTSV():

    with open("./output/final/data/shanghai_final.tsv","r",encoding="UTF-8") as f_in:
          file_list = csv.reader(f_in, 'mydialect')
          for line in file_list:
              print(line)
    pass


def TT(line):

    id = []
    city = []
    Shopname = []
    lng = []
    lat = []
    type = []
    comments = []
    scores = []
    recomment = []

    id.append(int(line[0]))
    city.append(line[1])
    Shopname.append(line[2])
    lng.append(float(line[3]))
    lat.append(float(line[4]))
    type.append(line[5])
    comments.append(int(line[6]))
    scores=line[7:10]


    l=len(line[10:])
    recomment = line[10:]

    if l<4:
        for i in range(l-1,2):
            recomment.append('')

    line_output = id + city + Shopname + lng + lat + type + comments + scores  + recomment

    return line_output



def ImportData(FileList):
    conn = psycopg2.connect(database='TasteAnalysis', user='postgres', password='123456', host='127.0.0.1', port='5432')
    cur = conn.cursor()
    # cur.execute("CREATE TABLE dianping_loc( id oid,"
    #             " city text, shopname text, lng text, lat text,type text, comment text,score1 text, score2 text, score3 text, rec1 text, rec2 text, rec3 text );")

    for filename in FileList:
        firstname,lastname=filename.split(".")
        city, mode = firstname.split('_')

        with open("./output/final/dianping_loc.tsv", "r", encoding="utf-8")as f_in:
            file_list = csv.reader(f_in, 'mydialect')
            i=0
            for line in file_list:
                tt=TT(line)

                print(tt)

                sql="INSERT INTO dianping_loc VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}' ) ".format(tt[0],tt[1],tt[2],tt[3],tt[4],tt[5],tt[6],tt[7],tt[8],tt[9],tt[10],tt[11],tt[12])
                # sql = "INSERT INTO test1 VALUES ('1','2','3','4','5','6','7','8','9','10') "
                cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

def Combine(FileList):
    i = 0
    for filename in FileList:
        firstname,lastname=filename.split(".")
        city, mode = firstname.split('_')
        city=Pinyin2Characters[city]
        with open("./output/final/loc/{}.tsv".format(firstname), "r", encoding="utf-8")as f_in,\
            open("./output/final/dianping_loc.tsv",'a',encoding="utf-8") as f_out:
            file_list = csv.reader(f_in, 'mydialect')

            for line in file_list:
                i+=1
                f_out.write(str(i)+"\t")
                f_out.write(city+"\t")
                print(i,end="\t")
                print(city,end="\t")

                # print(line)
                for item in line[2:]:
                    print(item,end="\t")
                    f_out.write(item+"\t")
                print()
                f_out.write("\n")



    pass


if __name__ == '__main__':

    rootdir = "./output/final/loc"

    # FileList=GetFile(rootdir)
    FileList = ['dianping_loc.tsv']
    # Verify(FileList)
    # Modify(FileList)
    # GetLoc(FileList)
    # line = ['1','1','椒鸣椒麻小馆(五道口店)','小吃快餐','8356','9.1','8.7','9.2','椒鸣凤仪椒麻鸡','椒鸣馕炒包包菜','椒鸣招牌辣爆小公鸡拌面']
    line = ['1', '1', "Friends' Cafe老友记主题店", '小吃快餐', '8356', '9.1', '8.7', '9.2','椒鸣凤仪椒麻鸡','']
    line2=['25002', '32', '亭子里’的家庭', '俄罗斯菜', '-1', '1.0', '2.0', '3.0', '椒鸣凤仪椒麻鸡','']


    # if is_number(line[])
    # ReadTSV()
    # print(line2[5:8])
    # out=TT(line2)
    # print(line[8])
    # print(out)
    ImportData(FileList)
    # Combine(FileList)

    # list=["1",""]
    # if list[0]:
    #     print(len(list))
    #
    # # 1	1	椒鸣椒麻小馆(五道口店)	小吃快餐    8356	9.1	8.7	9.2	椒鸣凤仪椒麻鸡	椒鸣馕炒包包菜	椒鸣招牌辣爆小公鸡拌面
    # line=['1','1','椒鸣椒麻小馆(五道口店)','小吃快餐','8356','9.1','8.7','9.2','椒鸣凤仪椒麻鸡','椒鸣馕炒包包菜','椒鸣招牌辣爆小公鸡拌面','','','']
    # result=Write(line)
    # print(result)
    # print(len(line))
    # print(len(result))
    pass