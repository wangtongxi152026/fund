import requests
import time
import json
import pandas as pd
import numpy as np

jsonIdx = 3
jsonData = []
fileJson = {}
with open('./store.json', "rb") as file:
    jsonData = json.load(file)
    fileJson = jsonData[jsonIdx]

# code = '005609'
# portion = 399.34
# start_cach = 177.84

code = fileJson['code']
portion = fileJson['portion']
start_cach = fileJson['start_cach']
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


def  round3(value):
    return str(round(value, 3) )

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
print(data.loc[data.index[0], 0])
# print(data)
res1 = requests.get(
    'http://fundgz.1234567.com.cn/js/{code}.js?'.format(code=code))
datasplite = json.loads(res1.text[8:-2])
print(res1.text[8:-2])

# ????????????
current_value = float(datasplite['gsz'])
jsonData[jsonIdx]['gsz'] = current_value
jsonData[jsonIdx]['name'] = datasplite['name']

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
print('cash', cash)
change = (current_value-float(value[0]))/float(value[0])*100
print('????????????:', current_time, '????????????:', current_value, 'Change:', change, '%')
print('??????????????????:', index, '??????5?????????:', latest_ma5, '????????????:', lastset_trend)

print(date1, value[0])
print(date2, value[1])

for idx, i in enumerate(value):
    time = [date1, date2][idx].split(' ')[0]
    buy_factor = 5.5
    sell_factor = 5
    ???????????? = 0
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
        ???????????? = round3(reaction*current_value)
    else:
        reaction = (float_value/current_value-1)*buy_factor*cash
        factor = buy_factor

    action = '???????????????' + round3(reaction) if(reaction > 0) else '????????????' + \
        str(reaction) + '???????????????' + ????????????

    print('??????{time}?????????:{action} ??????: {factor}'.format(
        time=time, action=action, factor=factor))

    if idx == 0:
        jsonData[jsonIdx]['action'] = reaction
        if 'sell_value' in jsonData[jsonIdx].keys():
            del jsonData[jsonIdx]['sell_value']
        if reaction < 0:
            jsonData[jsonIdx]['sell_value'] = ????????????

with open("./store.json", "w", encoding='utf-8') as dump_f:
    json.dump(jsonData, dump_f, ensure_ascii=False)
