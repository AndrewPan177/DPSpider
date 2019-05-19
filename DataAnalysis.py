#-*-coding:utf-8-*-
import re
import json
import time
import sys
import os
import os.path
import csv
import jieba
from collections import Counter
#import xlrd



'''
餐饮大数据可视化大纲：

1.城市餐馆位置分布
    以散点图形式，显示各家参观在城市的具体位置分布。同时还可以通过热力图展现出城市商圈的分布特征。
    仅显示 武汉、北京、上海这三座城市
    散点图：在地图上显示出各个餐馆的位置，点击图标，弹窗中显示店铺的 店名、经纬度、三项评分 推荐菜
        需要 city_loc.tsv数据，将数据传入，
        读取 shopname type score lng lat rec 在地图上点击显示
        使用百度地图api完成
    热力图：需要 dianping_loc.tsv数据
        仅需读取 lng 和 lat
        暂定百度地图api，如有需要可以更换

2.分店最多的餐厅
    以柱状图或其他统计图表，根据jiaba或者python原生方法，获取词频最高的商店名，即分店最多商店
    需要 dianping_final.tsv数据
        读取店铺名,通过已有函数进行数据清洗，获取店铺出现次数
        暂定chart.js

3.各个城市商店类别对比：
    以柱状图或其他统计图表，获取词频最高的店铺类型
    需要dianping_final.tsv数据
        读取店铺类别,通过已有函数进行数据清洗，获取店铺类别出现次数
        暂定chart.js
    
4.各个城市三项评分汇总
    以多系列柱状图的形式，得到每个城市所有店铺三项评分的的平均值
    需要dianping_final.tsv数据
        使用funsioncharts.js
        没学会django板块


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

CookingStyle=['炒','煎','贴','炸','熘','烹','焖','烧','氽','蒸','酥','烩','扒','炖','爆','煮'
    , '煨','卤','酱','烤','腌','拌','焗']
'''
南昌：螺蛳 粉 臭豆腐 绝味 火锅 酱爆 酱 卤 愤怒 夫妻肺片 毛血旺 爆炒 
长沙：口味 粉 臭豆腐 绝味 火锅 酱爆 酱 卤
贵阳：红汤 
'''
# 单‘川’字无法判别，还需要对同一道菜的其他字段进行识别
# 川+肠、香、味、麻、四、式、斗
chuan=['肠','香','味','麻','四','斗','火锅']
nanchang=['螺蛳','粉','臭豆腐','绝味','火锅','酱','愤怒','毛血旺','爆炒','火锅']
changsha=['口味','绝味','火锅','卤','酱爆']
guiyang=['红汤','臭豆腐','绝味','宫爆','宫保','爆','卤','炝','毛血旺','火锅','酱','凉拌']
chuanyu=['火锅','爆']
Hot=['椒','辣','麻婆','川','蜀','油泼','红油','湘','牛蛙','愤怒','夫妻肺片']

'''
对店铺+评分+推荐菜的列表进行遍历
若三道菜中某一道菜被识别为辣
    辣度值+=1      # 不加了不加了 二值化了
得出辣度值列表

遍历辣度值列表，

'''


# 判断是否为数字
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


# 辣度值计算
def GetHotVal(line,f_out,city):
    recomments=[]
    if line[8]:
        recomments += line[8:]

    if city=='nanchang':
        HotDish=Hot+nanchang
    elif city=='guiyang':
        HotDish=Hot+guiyang
    elif city=='changsha':
        HotDish=Hot+changsha
    elif city=='chongqing' or city=='chengdu':
        HotDish=Hot+chuanyu
    else:
        HotDish=Hot


    hot_val=0
    for food in recomments:
        f=[]
        for h in HotDish:
            m=re.search(h,food)
            if m :
                f.append(m.group())
                hot_val+=1
                break

        # 如果含有“川”字
        cz=''
        for f_ in f:
            cz=re.search('川',f_)
        if cz:
            cout=0
            for c_ in chuan:
                # 在食物中表明川菜是辣的
                m=re.search(c_,food)
                if m :
                    cout+=1
            if cout==0:
                hot_val-=1


    # # 仅将辣度二分
    if hot_val:
        hot_val=1

    f_out.write(line[0]+"\t"+line[2]+"\t"+line[5]+"\t"+str(hot_val)+"\n")
    # print(line[0]+line[2]+line[5]+hot_val)




def Search(lines,CookingStyleScore,CookingStyleNum):


    for item in lines[8:11]:
        for cs in CookingStyle:
            for ch in item:
                if ch==cs and is_number(lines[5]):
                    # print(type(lines[5]))
                    # print(type(float(lines[5])))

                    CookingStyleScore["{}".format(cs)]+=float(lines[5])
                    CookingStyleNum["{}".format(cs)]+=1


    pass

# 辣度指数计算
def GetIndex(score,hot_val):
    # print(len(score),len(hot_val))

    hot_sum=0
    all=0


    for i in range(len(score)):
        if int(hot_val[i])>0:
            hot_sum+=float(score[i])*float(hot_val[i])
        all+=float(score[i])

    # print(str(hot_sum)+"\t"+str(all))

    index=hot_sum/all
    return index
    # pass


# 将城市的辣度值转化为辣度指数
def GetCityHotIndex(fileList):
    for filename in fileList:
        firstname, lastname = filename.split(".")
        city, mode = firstname.split('_')
        with open("./output/cookstyle/hot/hot_modify/{}.tsv".format(firstname), "r", encoding="utf8")as f_in, \
                open("./output/cookstyle/hotVal.tsv".format(city), "a", encoding="utf-8") as f_out:
            file_list = csv.reader(f_in, 'mydialect')
            score=[]
            hot_val=[]
            for line in file_list:
                score.append(line[2])
                hot_val.append(line[3])


            index=GetIndex(score,hot_val)


            f_out.write(city+"\t")
            f_out.write(str(index)+"\n")

            print("{} is {}".format(city,index))

# 获取城市的辣度值
def GetTaste(fileList):
    for filename in fileList:
        firstname, lastname = filename.split(".")
        city, mode = firstname.split('_')
        with open("./output/final/{}.tsv".format(firstname), "r", encoding="utf8")as f_in, \
                open("./output/cookstyle/hot/hot_modify/{}_hot.tsv".format(city), "w", encoding="utf-8") as f_out:
            file_list = csv.reader(f_in, 'mydialect')

            for line in file_list:

                GetHotVal(line,f_out,city)
            print("{} is finish.".format(city))



# 获取城市的所有推荐菜
# 我为啥要写这个函数啊2333
def GetCookStyle(fileList):

    for filename in fileList:
        firstname, lastname = filename.split(".")
        city,mode=firstname.split('_')
        with open("./output/final/{}.tsv".format(firstname), "r", encoding="utf8")as f_in, \
                open("./output/cookstyle/{}.tsv".format(city), "w", encoding="utf-8") as f_out:

            file_list = csv.reader(f_in, 'mydialect')

            recomments=[]
            # 将所有店铺的推荐菜都存放在一个列表里，然后将这个列表输出到对应城市的文件中
            for line in file_list:
                if line[8]:
                    recomments+=line[8:]
                    for li in line[8:]:
                        f_out.write(li+"\t")
                    f_out.write("\n")

            print("{} is finish.".format(city))


# 获取文件夹内的所有文件名
def GetFile(rootdir):
    FileList=[]
    for parent, dirnames, filenames in os.walk(rootdir):  # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:
            FileList.append(filename)
    # print(FileList)
    return FileList

# 对读到的辣度指数进行归一化
def Normalization():

    hotVal=dict()
    hotVal_Nor=dict()
    index=[]
    with open('./output/CookStyle/hotVal.tsv','r',encoding='utf-8') as f_in:
        with open('./output/CookStyle/hotVal_Nor.tsv','w',encoding='utf-8')as f_out:
            file_list = csv.reader(f_in, 'mydialect')
            for line in file_list:
                hotVal[line[0]]=line[1]
                index.append(line[1])
            # 对指数进行正序排序
            index.sort()

            min=float(index[0])
            max=float(index[-1])

            for key in hotVal:
                x=float(hotVal[key])
                x_=(x-min)/(max-min)
                hotVal_Nor[key]=x_

            for key in hotVal_Nor:
                f_out.write(key+"\t"+str(hotVal_Nor[key])+"\n")
                print(key+"\t"+str(hotVal_Nor[key]))



def GetFendian(line,shopList):
    # shopname = '坚果印象野生板栗'
    shopname=line[2]
    # shopList = []
    m = re.search('[(]', shopname)
    if m:
        # print(m)
        dianpu, fendian1 = re.split("[(]", shopname)
    else:
        # print(1)
        dianpu = shopname
        fendian1 = ''
    shopList.append(dianpu)

    print(dianpu)

def Fendian(fileList):

    for filename in fileList:
        firstname, lastname = filename.split(".")
        city,mode=firstname.split('_')

        shopList=[]
        with open('./output/final/data/{}.tsv'.format(firstname),'r',encoding='utf-8')as f_in,\
                open('./output/analysis/{}_analysis.tsv'.format(city),'w',encoding='utf-8')as f_out:
                    file_list = csv.reader(f_in, 'mydialect')
                    for line in file_list:
                        print(city)
                        print(line[0])
                        GetFendian(line,shopList)

                    for item in shopList:
                        f_out.write(item+"\n")

# 词频统计
def get_words(txt):
    seg_list = jieba.cut(txt)
    c = Counter()
    for x in seg_list:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    print('常用词频度统计结果')
    for (k,v) in c.most_common(100):
        print('%s   %d' % ( k, v))




def ShopAnalysis(fileList):


    # filelist是存储一个文件夹中所有文件文件名的列表
    # 遍历这个列表，获取每一个文件名   eg:wuhan_analysis.tsv
    for filename in fileList:
        firstname, lastname = filename.split(".")   # 对文件名进行分割  分为  wuhan_analysis  和   tsv
        city,mode=firstname.split('_')          # 对文件名 以 “_” 来分割，分为  wuhan   和  analysis

        # 打开文件
        with open('./output/analysis/{}.tsv'.format(firstname),'r',encoding='utf-8') as f_in,\
                open('./output/analysis/result/{}_result.tsv'.format(city),"w",encoding="utf-8") as f_out:
            # file_list = csv.reader(f_in, 'mydialect')
            # 读文件，tsv文件的读取有两种方式，一种是上面的，一种是下面的。下面的读取为一个str对象
            data=f_in.read()
            # get_words(data)
            # 建立存放词频的字典
            frequency={}

            #
            shop=data.split("\t")

            for shopname in data.split("\n"):
                # print(shopname)
                if shopname not in frequency:
                    frequency[shopname]=1
                else:
                    frequency[shopname]+=1

            # 对字典进行排序
            A = sorted(frequency.items(), key=lambda frequency: frequency[1], reverse=True)

            for item in A:
                for i in item:
                    f_out.write(str(i)+"\t")
                    # print(i,end="\t")
                # print()
                f_out.write("\n")

            print("{} is finish.".format(city))


# 将xlsx数据转化为JSON数据
'''
{
        "name": "北京",
        "value": [116.404158,39.910072],
        "symbolSize": 2,
        "itemStyle": {
            "normal": {
                "color": "#F58158"
            }
        }
}



'''
def xlsx2JSON1():

    data=[]
    with open("./data/location.csv","r",encoding="utf-8") as f_in:
        file_list = csv.reader(f_in, 'mydialect')
        for line in file_list:
            temp=line[0].split(",")
            data.append(temp)
    f_in.close()

    dataall=[]
    temp=[]
    for item in data:
        temp.append(item[0])
        temp.append(item[1][1:])
        temp.append(item[2][0:-1])
        temp.append(item[3])
        dataall.append(temp)
        temp=[]

    return dataall
    # print(dataall)
    # with open("./output/JSON/file1.JSON","w",encoding="utf-8") as f_out:
    #     for line in dataall:
    #         color='#53868B'
    #         if line[3]=='8':
    #             color='#FF6A6A'
    #         #}"\n\t\t}\n\t}'
    #
    #         f_out.write("{\n")
    #         f_out.write('\t"name":"{}",\n\t"value":[{},{}],\n\t"symbolSize":{},\n'.format(line[0],line[1],line[2],line[3]))
    #         f_out.write('\t"itemStyle": {\n\t\t"normal": {\n\t\t\t"color": "'+color+'"\n\t\t}\n\t}')
    #         f_out.write("\n},")
    #         # print("{")
    #         # print('\t"name":"{}",\n\t"value":[{},{}],\n\t"symbolSize":{},'.format(line[0],line[1],line[2],line[3]))
    #         # print('\t"itemStyle": {\n\t\t"normal": {\n\t\t\t"color": "'+color+'"\n\t\t}\n\t}')
    #         # print("},")
    #          # print(line)
    # f_out.close()



'''
{
        "fromName": "北京",
        "toName": "上海",
        "coords": [
            [116.404158,39.910072],
            [121.475605,31.223183]
        ],
        "value":78796
}
'''

def csv2JSON(filelist,loc):


    # 用来存放地名和坐标的字典

    NoneList = []
    for filename in filelist:
        firstname, lastname = filename.split(".")
        # print(firstname)

        with open("./data/出/{}".format(filename),"r",encoding="gbk")as f_in,open("./output/JSON/fileOut2.JSON","a",encoding="utf-8")as f_out:
            file_list = csv.reader(f_in, 'mydialect')
            for line in file_list:
                fromname,toname,value=line[0].split(",")
                print("{")
                f_out.write("{\n")
                if fromname not in loc or toname not in loc:
                    print('\t"fromname":"{}",\n\t"toname":"{}",\n\t"coords":[\n\t\t[{},{}],\n\t\t[{},{}]\n\t],\n\t"value":{}'.format(
                        fromname,toname,
                        '0.0',
                        '0.0',
                        '0.0',
                        '0.0',
                        int(float(value))))
                    f_out.write(
                        '\t"fromname":"{}",\n\t"toname":"{}",\n\t"coords":[\n\t\t[{},{}],\n\t\t[{},{}]\n\t],\n\t"value":{}\n'.format(
                             fromname,toname,
                            '0.0',
                            '0.0',
                            '0.0',
                            '0.0',
                            str(int(float(value)))))
                    NoneList.append(fromname)
                    NoneList.append(toname)
                else:
                    print('\t"fromname":"{}",\n\t"toname":"{}",\n\t"coords":[\n\t\t[{},{}],\n\t\t[{},{}]\n\t],\n\t"value":{}'.format( fromname,toname,

                                                                                                  loc[fromname][0],
                                                                                                  loc[fromname][1],
                                                                                                  loc[toname][0],
                                                                                                  loc[toname][1],
                                                                                                  int(float(value))))
                    f_out.write('\t"fromname":"{}",\n\t"toname":"{}",\n\t"coords":[\n\t\t[{},{}],\n\t\t[{},{}]\n\t],\n\t"value":{}\n'.format( fromname,toname,
                                                                                                  loc[fromname][0],
                                                                                                  loc[fromname][1],
                                                                                                  loc[toname][0],
                                                                                                  loc[toname][1],str(int(float(value)))))
                print("},")
                f_out.write("},\n")
                # print(line[0])

    print(NoneList)

    # print(dataall)


    pass

'''
{name:'北京',datas:['4','3','4','5','5','6','6','7','星巴克','133','222','120','333','100','444','90','555','80','666','70','777','60','888','50','999','32','10','12']},

4	3	4	5	5	6	6	7
data=[
    [4,3,4,5,5,6,6,7],
    [4,3,4,5,5,6,6,7],
]
citylist=["北京","长春"]

'''
data=[[4,3,4,5,5,6,6,7],[3,3,5,3,10,6,4,7],[8,8,1,4,2,10,2,8],[10,10,3,3,4,7,0,4],[9,9,1,4,0,8,1,4],
[1,1,3,7,2,4,4,1],[0,2,2,6,6,2,10,2],[6,7,7,5,3,4,2,6],[4,4,4,4,9,3,3,6],[1,1,3,6,2,0,4,1],[2,2,4,9,4,3,4,0],
[4,1,2,4,5,6,3,4],[4,2,1,3,4,5,1,6],[3,4,5,3,5,6,2,10],[6,3,6,2,1,4,5,7],[5,2,4,1,4,2,3,3],[5,3,2,2,3,5,4,5],
[7,6,3,4,2,9,7,4],[3,3,2,9,5,7,5,4],[6,0,9,2,1,5,3,3],[2,4,4,10,2,7,6,1],[5,4,3,2,9,4,4,9],[4,1,2,3,6,6,5,6],
[3,1,8,4,8,4,6,6],[3,3,2,3,4,5,7,9],[7,6,2,3,3,8,4,3],[4,4,0,0,5,3,5,2],[6,7,10,2,3,6,8,5],[4,4,5,3,1,7,4,5],
[3,6,2,2,3,5,3,2],[3,4,2,2,4,6,4,5],
]
citylist=['北京','长春','长沙','成都','重庆','福州','广州','贵阳','哈尔滨',
          '海口','杭州','合肥','呼和浩特','济南','昆明','兰州','拉萨','南昌',
          '南京','南宁','上海','沈阳','石家庄','太原','天津','武汉','乌鲁木齐','西安','西宁','银川','郑州',
]
# help华姐
def helphuasister(filelist):
    for filename in filelist:
        firstname, lastname = filename.split(".")
        city,a=firstname.split("_")
        with open("./output/analysis/result/{}.tsv".format(firstname),"r",encoding="utf-8")as f_in,open("./output/analysis/huajie/output.txt".format(city),"a",encoding="utf-8")as f_out:


            no=0
            city_chara = Pinyin2Characters[city]
            for j in range(len(citylist)):
                if citylist[j] == city_chara:
                    no = j
            taste = data[no]


            f_out.write("{ ")
            f_out.write("name:\'{}\',datas:[".format(city_chara))

            for t in taste:
                f_out.write("\'{}\',".format(t))

            i = 0
            file_list = csv.reader(f_in, 'mydialect')
            for line in file_list:
                if i<19:
                    shopname = line[0]
                    num = line[1]
                    f_out.write("\'{}\',\'{}\',".format(shopname,num))
                elif i==19:
                    shopname = line[0]
                    num = line[1]
                    f_out.write("\'{}\',\'{}\'".format(shopname, num))
                else:
                    break

                i+=1

            f_out.write("]},\n")


    pass



def helpLaowang():
    with open("./data/bou1_4l.JSON","r",encoding="utf-8")as f,open("output2.txt","w",encoding="utf-8")as f_out:
        data = json.load(f)
        for item in data["features"]:
            f_out.write(str(item["geometry"]["coordinates"])+"\n")
            print(item["geometry"]["coordinates"])


if __name__ == '__main__':

    rootdir1="./output/analysis/result"
    # rootdir2 = "./output/CookStyle/hot/hot_modify"
    FileList1=GetFile(rootdir1)
    # FileList1=['wuhan_analysis.tsv']
    # FileList2 = GetFile(rootdir2)
    # print(FileList1)
    # 以下四个函数都是求辣度指数特征向量的

    # helphuasister(FileList1)
    helpLaowang()



    # 将xlsx 修改为JSON
    # dataall=xlsx2JSON1()
    #
    #
    #
    #
    # loc = dict()
    #
    # for lines in dataall:
    #     # print(lines)
    #     loc[lines[0]] = [lines[1], lines[2]]
    # #
    # # print(loc['遵义'][0])
    # #
    # csv2JSON(FileList1,loc)
    #
    # a='123.4253'
    # print(type(a))
    # b=int(float(a))
    # print(b)


    # shopname='魔王烧肉 ox deamon king'
    # shopList=[]
    # m=re.search('[(]',shopname)
    # if m:
    #     print(m)
    #     dianpu,fendian1=re.split("[(]",shopname)
    # else:
    #     # print(1)
    #     dianpu=shopname
    #     fendian1=''
    # shopList.append(dianpu)
    #
    # print(dianpu,fendian1)







