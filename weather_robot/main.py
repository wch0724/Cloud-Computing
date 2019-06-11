#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nluapi import NluAPISample
import argparse
import json
import requests
import json
import argparse
import re
import urllib
from citycode import citycode
import datetime

#获取本机ip地址
def get_ip():
    try:
        res = requests.get("http://txt.go.sohu.com/ip/soip") #搜狐免费的ip地址查询接口
        ip = re.findall(r'\d+.\d+.\d+.\d+',res.text)[0] 
    except:
        print('Network error, get ip failed...')
    return ip


#由本机ip地址获取当前城市
def get_locate_info(ip):
    try:
        # get mapping from IP to address using taobao
        url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s" % ip
        res = requests.get(url=url)
        #print(res.text)
        info = json.loads(res.text) #将json格式转换为字典
        # print(info, type(info))
        # print("IP:%s" % info["data"]["ip"])
        # print("国家:%s" % info["data"]['country'])
        # print("城市:%s" % info["data"]["city"])
        # print("地区:%s" % info["data"]["county"])
        # print("运营商:%s" % info["data"]["isp"])
        # print("运营商id:%s" % info["data"]["isp_id"])
    except:
        print('Network error, get locate info failed')
    return info["data"]["city"]


def get_weather(city,date='',intent=''):
    date_map = {
        '今天': datetime.date.today().day,
        '明天': (datetime.date.today() +  datetime.timedelta(days=1)).day,
        '后天': (datetime.date.today() +  datetime.timedelta(days=2)).day,
        '大后天': (datetime.date.today() +  datetime.timedelta(days=3)).day,
    }

    #使用城市代码查询天气
    weather=dict()
    try:
        url = 'http://t.weather.sojson.com/api/weather/city/{}'.format(citycode[city])     # 申明URL字符串
    except:
        print('您查询的不是中国城市哦！')
    user_agent = {'User-agent': 'Mozilla/5.0'}
    res = requests.get(url=url,headers = user_agent)
    info = json.loads(res.text)

    if(date.find("月") == -1): #如果问法是今天/明天/后天/大后天
        date_day = str(date_map[date]).zfill(2) #如果日期是个位数则在前面补0
    else:  #如果问法是x月x日或x月x号
        month_loc = date.find("月")
        if(date.find("日") == -1):
            day_loc = date.find("号")
        else:
            day_loc = date.find("日")
        input_day = date[month_loc + 1:day_loc] #取出月和日之间的值作为日期
        date_day = str(input_day).zfill(2) #如果日期是个位数则在前面补0
    #print(date_day)

    for day_forecast in info['data']['forecast']:
        if day_forecast['date'] == date_day:
           weather = day_forecast
    weather['city'] = city

    if intent == r'查询天气':
        print('{}{},{},{},{},{}'.format(
            weather['ymd'] + weather['week'],
            weather['city'],
            weather['type'],
            weather['low'] + weather['high'],
            weather['fx'] + weather['fl'],
            weather['notice']
        ))
    elif intent == r'查询温度':
        print('{},{},{}'.format(
                                         weather['ymd'] + weather['week'],
                                         weather['city'],
                                         weather['low'] + weather['high']
                                         ))
    elif intent == r'查询风速':
        print('{},{},{}'.format(
                                     weather['ymd'] + weather['week'],
                                     weather['city'],
                                     weather['fx'] + weather['fl']
                                     ))
    elif intent == r'查询云量':
        print('{},{},{}'.format(
                                     weather['ymd'] + weather['week'],
                                     weather['city'],
                                     weather['type']
                                     ))
    elif intent == r'查询出行建议':
        print('{},{},{}'.format(
                                     weather['ymd'] + weather['week'],
                                     weather['city'],
                                     weather['notice']
                                     ))
    return weather

class Session:
    url = ''
    appKey = ''
    appSecret = ''
    nluApi = None
    params = {'date':None,'locate':None}

    def __init__(self,appKey,appSecret, url = 'https://cn.olami.ai/cloudservice/api'):
        self.appKey = appKey
        self.appSecret = appSecret
        self.url = url
        self.nluApi = NluAPISample()
        self.nluApi.setLocalization(self.url)
        self.nluApi.setAuthorization(self.appKey, self.appSecret)     

    def reset(self):
        self.params = {'date':None,'locate':None,'intent':None}

    def request(self,inputText):
        # print("\n---------- Test NLU API, api=nli ----------\n");
        response = self.nluApi.getRecognitionResult(self.nluApi.API_NAME_NLI, inputText)  #返回inputText的nlu识别结果
        response = json.loads(response)
        
        print(response)

        if response["status"] != "ok":
            print('Failed at connection... please check the network and configuration...')
            return False

        #取date和locate字段
        for slot in response["data"]["nli"][0]['semantic']:
                for attribute in slot['slots']:
                    self.params[ attribute['name'] ] = attribute['value']  
        #如果data和date的值不存在，则需要进行多轮对话补全信息
        if self.params['locate'] == None or self.params['date'] == None:
            raise TypeError('data missing')

        #取intent字段
        try:
            for slot in response["data"]["nli"][0]['semantic']:
                self.params['intent'] = slot['modifier'][0] 
        except:
            if self.params['locate']!=None and self.params['date']!=None:
                self.params['intent'] = '查询天气'
        return self.params

        # try:
        #     for attribute in response["data"]["nli"][0]["data_obj"]:
                
        #         if attribute['is_querying'] == False: continue
        #         answer_info = dict()
        #         answer_info["time"] = attribute['description'].split(',')[0]
        #         answer_info['location'] = attribute['city']
        #         answer_info['intent'] = attribute['description'].split(',')[1]
        #         answer_info['temperature'] =  attribute['description'].split(',')[3] +' '+ attribute['description'].split(',')[4]
        #         answer_info['wind'] =  attribute['description'].split(',')[2]
        #         answer = '{}{}'.format(answer_info['location'], answer_info["time"])
        #         for k in self.keys1:
        #             if k in question:
        #                 print(k,'=?',question)
        #                 answer += answer_info['wind']
        #         for k in self.keys2:
        #             if k in question:
        #                 answer += answer_info['temperature']
        #         return answer,answer_info
        # except:
        #     answer = response["data"]["nli"][0]["desc_obj"]['result']
        #     return answer,None
        #     #print('对不起我无法理解您的话')
        

if __name__ == '__main__':

    flag_data = 0 #如果信息不全，flag为0，否则为1

    ip = get_ip() #获取本机ip
    city = get_locate_info(ip) #由本机ip获取当前城市
    session = Session(appKey = 'e1737f546a6f45cfbb52d31118acc2d7', appSecret = 'ffcb9cb5b5ee46d79035a91e5f07ca9c' )
    question = r'{}今天天气'.format(city)
    # answer,answer_info = 
    params = session.request(question)
    session.reset()

    get_weather(params['locate'],params['date'],params['intent'])
    
    # print(answer_info)
    flag_data = 1

    while True:

        if flag_data == 1:
            print("\n请问有什么可以帮助您？")
        else:
            pass

        question = input()
        try:
            params = session.request(question)
            if params['locate'] != None and params['date'] != None:
                get_weather(params['locate'],params['date'],params['intent'])
                session.reset()
                flag_data = 1
        except TypeError:
            print('请补全查询信息地点和时间')
            flag_data = 0
        except:
            print('我现在不够聪明 可以重新说一下吗？')
