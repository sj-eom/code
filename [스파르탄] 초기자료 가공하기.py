#%%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import math
import glob
from matplotlib.colors import ListedColormap
from sklearn.metrics import r2_score
import scipy.stats
import numpy.ma as ma
import seaborn as sns
pd.set_option('mode.chained_assignment',  None) # 경고 off
#%%

site = 'aeronet_seoul'
site = 'aeronet_yonsei'
site = 'aeronet_unist'

path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/'
# path = '/Users/eomsujin/OneDrive - UNIST/SPARTAN/'

#%%
aeronet = glob.glob(path+site+'/'+'*'+'new_parameter.csv')[0]
spartan_25 = path+'FilterBased_ReconstrPM25_KRUL (10).csv' #KRSE - 6 (12월), 7 (2월28) #KRUL - 9 (12월), 10(2월28)

#%%################기초 데이터 생성-날짜인덱스####################################
data_org = pd.read_table(spartan_25,sep=",", skiprows=1)#,usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,\
data = data_org.copy()                                   # 17,18,19,20,21,22,23,24])

#%%##############필터 별 정렬 위해서 새로운 인덱스 만들기###################
data['index_number'] = np.nan
data['start_end_time'] = np.nan
data['date'] = np.nan
data['end_date'] = np.nan
f_list = []
#%%
filter_id = np.unique(data_org.Filter_ID) #필터 각각 번호
id_size = np.size(filter_id) #필터 총 개수
grouped = data_org.groupby('Filter_ID')
max_size = np.max(grouped.size()) # 필터별 파라미터 최대 개수, 아마도 9
################Search full df################
for filter_s in filter_id:                          #필터 1번부터 끝까지
    search_s = data[data['Filter_ID']==filter_s]    #필터아이디 같은거끼리 모음 = 각 필터별의 데이터 bc, sulfate 등등
    if np.shape(search_s)[0] == max_size:           #파라미터 수가 max와 같으면
        full_df = search_s.copy()                   #처음으로 max인 필터의 데이터 모두 저장
        break
#%%
for filter_n in filter_id:   #필터 1번부터 끝까지
    print(filter_n)
    search = data[data['Filter_ID']==filter_n]
    if np.shape(search)[0] == max_size:             #파라미터 개수 풀이면 넘어감
        continue
    else:
        full_df_search = full_df.copy()             #파라미터 개수 부족하면 

        for k in range(0,np.shape(search)[0]):      #파라미터 개수 부족한 그 데이터에서 
            search_product = search.Parameter_Code.iloc[k] #각각 파라미터 하나씩 읽음
            exist_index = full_df_search[full_df_search.Parameter_Code == search_product].index[0] #읽은 파라미터의 원래 인덱스번호
            full_df_search = full_df_search.drop(exist_index) #얘들이 존재하는 인덱스 번호를 풀 df에서 제거함
            
        full_df_search.Filter_ID = filter_n #존재 안하는 파라미터 줄만 뽑아서 필터이름 동일하게 설정하고 데이터는 없게함.
        full_df_search.Value=np.nan
        
        data = data.append(full_df_search) #새로 만들어진 보충용 파라미터 추가함! 따라서 데이터 수는 총 9xfilter id개수
#%%
parameter_list = pd.DataFrame(full_df.Parameter_Code).reset_index().Parameter_Code
parameter_name_list = pd.DataFrame(full_df.Parameter_Name).reset_index().Parameter_Name
for t in range (0, np.size(data.index)):
    for h in range (0, np.size(parameter_list)):

        if data['Parameter_Code'].iloc[t] == parameter_list[h] :#Filter PM2.5 mass
            data['index_number'].iloc[t] = parameter_list.index[h] #인덱스 넘버 순서대로 1~9까지 지정해줌
        
        if data['Units'].iloc[t] == 'Nanograms per cubic meter (ng/m3)':
            data['Units'].iloc[t] = 'Micrograms per cubic meter (ug/m3)'
            data['Value'].iloc[t] = data['Value'].iloc[t]/1000
       
#%%        
###################날짜세팅(의미없음)######
for i in range (0,np.size(data.index)):
    data['date'].iloc[i] = str(data['Start_Year_local'].iloc[i])+'-'+str(format(data['Start_Month_local'].iloc[i],'02'))+'-'+str(format(data['Start_Day_local'].iloc[i],'02'))
    data['end_date'].iloc[i] = str(data['End_Year_local'].iloc[i])+'-'+str(format(data['End_Month_local'].iloc[i],'02'))+'-'+str(format(data['End_Day_local'].iloc[i],'02'))
##################sort 정렬##############
data = data.sort_values(by=['Filter_ID','index_number'] ,ascending=True) #필터번호와 파라미터 인덱스로 정렬
data = data.reset_index(drop=True)
#%%
# # ## 9 = max_size
for j in range (0, np.size(filter_id)):
    globals()['period'+str(j)] = pd.DataFrame([data['Value'][max_size*j+0:max_size*j+max_size]]) #9개씩 끊어서 나눔
    globals()['period'+str(j)].columns = [data['Parameter_Name'][max_size*j+0:max_size*j+max_size]]
        
    f_list.append(globals()['period'+str(j)]) #필터수만큼의 풀 데이터프레임 각각 제작
#날짜리스트    
day_list = np.unique(data.date)
day_list = pd.to_datetime(day_list)

end_list = np.unique(data.end_date)
end_list = pd.to_datetime(end_list)

#병합
f = np.vstack(f_list)
f = pd.DataFrame(f)
f.columns = parameter_name_list
f.index = pd.DatetimeIndex(day_list)
f['filter_name'] = filter_id
f['end_date'] = end_list

# f.to_csv(path+'aeronet_unist/spartan_unist_1.csv')
