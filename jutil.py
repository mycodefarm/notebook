import requests
import pandas as pd
import json

url = 'http://localhost:8081/test/data'
def load_data(sql):
    '''
    从服务器访问数据
    传入sql
    返回list(json)
    '''
    param = {'sql':sql}
    re = requests.get(url,params=param)
    data = re.json()['data']
    return data

def load_pd_df(sql):
    '''
    返回pandas的DataFrame
    '''
    return pd.DataFrame(load_data(sql))

def dump_obj(path, obj):
    '''先清空再保存对象到文件'''
    with open(path, 'w') as f:
        json.dump(obj, f, ensure_ascii=False)


def load_dumped_file(path):
    '''
    从文件加载对象
    :param path:
    :return:
    '''
    try:
        with open(path, 'r') as f:
            obj = json.load(f)
            return obj
    except:
        return None