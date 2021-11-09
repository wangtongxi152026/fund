import requests
import time
import json
import pandas as pd
import numpy as np
# from openpyxl.utils.dataframe import dataframe_to_rows
# from openpyxl import Workbook


def resolve():
    file = open('./store.json', "rb")
    fileJson = json.load(file)[2]
    code = fileJson["code"]
    portion = fileJson["portion"]
    start_cach = fileJson["start_cach"]
    return {'code': code, 'portion': portion, 'start_cach': start_cach}


# code = '005609'
# portion = 399.34
# start_cach = 177.84
# start = '2021-07-01'
code = resolve()['code']
portion = resolve()['portion']
start_cach = resolve()['start_cach']
start = '2021-07-01'
current_time = time.strftime('%Y-%m-%d', time.localtime())

value = [[] for a in range(2)]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}
url = 'http://stock.finance.sina.com.cn/fundInfo/api/openapi.php/CaihuiFundInfoService.getNav?symbol={code}&datefrom={start}&dateto={current_time}&page=1'.format(
    code=code,
    start=start,
    current_time=current_time,
)
info = requests.get(url, headers=headers).json()


def create_data():
    dic = {}
    for i in range(20):
        try:
            ljjz = float(info['result']['data']['data'][i]['ljjz'])
            date = info['result']['data']['data'][i]['fbrq']
        except IndexError:
            pass
        dic[date] = ljjz

    df = pd.DataFrame(dic.values(), index=dic.keys())
    df['ma5'] = np.nan
    df['trend'] = np.nan

    for i in range(len(df)-1):
        df.loc[df.index[i], 'ma5'] = df[0][i:i+5].mean()
        df.loc[df.index[i-1], 'trend'] = df.loc[df.index[i-1], 'ma5'] / \
            df.loc[df.index[i], 'ma5']-1
    return df


data = create_data()
# print(data)
index = 0
for i in range(18, 0, -1):
    if data.loc[data.index[i], 'trend']*data.loc[data.index[i+1], 'trend'] < 0:
        index = i

total_latest_4_sum = (data.loc[data.index[0], 0]
                      + data.loc[data.index[1], 0]
                      + data.loc[data.index[2], 0]
                      + data.loc[data.index[3], 0])

res1 = requests.get(
    'http://fundgz.1234567.com.cn/js/{code}.js?'.format(code=code))
datasplite = json.loads(res1.text[8:-2])
print(res1.text[8:-2])

# 估算净值
current_value = float(datasplite['gsz'])
latest_ma5 = round((total_latest_4_sum+current_value)/5, 4)
lastset_trend = round((latest_ma5/data.loc[data.index[0], 'ma5']-1), 4)
if lastset_trend*data.loc[data.index[0], 'trend'] > 0:
    index += 1
else:
    index = 1

total_value = info['result']['data']['data']
date1 = total_value[0]['fbrq'].split(' ')[0]
value[0] = total_value[0]['jjjz']
date2 = total_value[1]['fbrq'].split(' ')[0]
value[1] = total_value[1]['jjjz']
cash = portion*float(value[1])
change = (current_value-float(value[0]))/float(value[0])*100
print('单日情况:', current_time, '估算净值:', current_value, 'Change:', change, '%')
print('趋势维持天数:', index, '最新5日均值:', latest_ma5, '最新趋势:', lastset_trend)

print(date1, value[0])
print(date2, value[1])

for idx, i in enumerate(value):
    buy_factor = 5.5
    sell_factor = 5
    if index > 11 and lastset_trend < 0:
        buy_factor = 10
        sell_factor = 5
    if index > 5 and lastset_trend < 0:
        buy_factor = 3
        sell_factor = 5
    if index > 5 and lastset_trend > 0:
        buy_factor = 5.5
        sell_factor = 0

    if cash < start_cach/2:
        buy_factor = 5.5
        sell_factor = 0
    if cash > start_cach*2:
        buy_factor = buy_factor/2
        sell_factor = sell_factor/2
    if cash > start_cach*3:
        buy_factor = buy_factor/1.5
        sell_factor = sell_factor/1.5
    if cash > start_cach*4:
        buy_factor = buy_factor/1.33
        sell_factor = sell_factor/1.33
    if cash > start_cach*5:
        buy_factor = buy_factor/1.25
        sell_factor = sell_factor/1.25
    float_value = float(i)

    if current_value > float_value:
        reaction = -(current_value/float_value-1)*sell_factor*portion
        factor = sell_factor
        print('相较于{time}的操作:卖出份额'.format(
            time=[date1, date2][idx].split(' ')[0]),  reaction, "系数:", factor)
    else:
        reaction = (float_value/current_value-1)*buy_factor*cash
        factor = buy_factor
        print('相较于{time}的操作:买入金额'.format(
            time=[date1, date2][idx].split(' ')[0]),  reaction, "系数:", factor)
