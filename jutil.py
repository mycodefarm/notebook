import requests
import pandas as pd

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

