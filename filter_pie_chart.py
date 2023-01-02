import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pytz 
import seaborn as sns
import math
pd.set_option('mode.chained_assignment',  None)
#%%///data loading///path : above;for window, below;for mac


#%%
path = 'C:/Users/PC/OneDrive - UNIST/spartan/'

#%%

spartan_yonsei = path+'FilterBased_ReconstrPM25_KRSE.csv'


#%%################기초 데이터 생성####################################
data_org_yonsei = pd.read_table(spartan_yonsei,sep=",", skiprows=1)#,usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,\
data_yonsei = data_org_yonsei.copy()                                   # 17,18,19,20,21,22,23,24])

#%%##############필터 별 정렬 위해서 새로운 인덱스 만들기###################
data_yonsei['index_number'] = np.nan
data_yonsei['start_end_time'] = np.nan
data_yonsei['date'] = np.nan

f_list_yonsei = []

#%%
filter_id_yonsei = np.unique(data_org_yonsei.Filter_ID) #필터 각각 번호
id_size_yonsei = np.size(filter_id_yonsei) #필터 총 개수


grouped_yonsei = data_org_yonsei.groupby('Filter_ID')
max_size_yonsei = np.max(grouped_yonsei.size()) # 필터별 파라미터 최대 개수, 아마도 9
################Search full df################
for filter_s_yonsei in filter_id_yonsei:                          #필터 1번부터 끝까지
    search_s_yonsei = data_yonsei[data_yonsei['Filter_ID']==filter_s_yonsei]    #필터아이디 같은거끼리 모음 = 각 필터별의 데이터 bc, sulfate 등등
    if np.shape(search_s_yonsei)[0] == max_size_yonsei:           #파라미터 수가 max와 같으면
        full_df_yonsei = search_s_yonsei.copy()                   #처음으로 max인 필터의 데이터 모두 저장
        break
#%%
for filter_n_yonsei in filter_id_yonsei:   #필터 1번부터 끝까지
    print(filter_n_yonsei)
    search_yonsei = data_yonsei[data_yonsei['Filter_ID']==filter_n_yonsei]
    if np.shape(search_yonsei)[0] == max_size_yonsei:             #파라미터 개수 풀이면 넘어감
        continue
    else:
        full_df_search_yonsei = full_df_yonsei.copy()             #파라미터 개수 부족하면 

        for k_yonsei in range(0,np.shape(search_yonsei)[0]):      #파라미터 개수 부족한 그 데이터에서 
            search_product_yonsei = search_yonsei.Parameter_Code.iloc[k_yonsei] #각각 파라미터 하나씩 읽음
            exist_index_yonsei = full_df_search_yonsei[full_df_search_yonsei.Parameter_Code == search_product_yonsei].index[0] #읽은 파라미터의 원래 인덱스번호
            full_df_search_yonsei = full_df_search_yonsei.drop(exist_index_yonsei) #얘들이 존재하는 인덱스 번호를 풀 df에서 제거함
            
        full_df_search_yonsei.Filter_ID = filter_n_yonsei #존재 안하는 파라미터 줄만 뽑아서 필터이름 동일하게 설정하고 데이터는 없게함.
        full_df_search_yonsei.Value=np.nan
        
        data_yonsei = data_yonsei.append(full_df_search_yonsei) #새로 만들어진 보충용 파라미터 추가함! 따라서 데이터 수는 총 9xfilter id개수

#%%
parameter_list_yonsei = pd.DataFrame(full_df_yonsei.Parameter_Code).reset_index().Parameter_Code
parameter_name_list_yonsei = pd.DataFrame(full_df_yonsei.Parameter_Name).reset_index().Parameter_Name

for t_yonsei in range (0, np.size(data_yonsei.index)):
    for h_yonsei in range (0, np.size(parameter_list_yonsei)):

        if data_yonsei['Parameter_Code'].iloc[t_yonsei] == parameter_list_yonsei[h_yonsei] :#Filter PM2.5 mass
            data_yonsei['index_number'].iloc[t_yonsei] = parameter_list_yonsei.index[h_yonsei] #인덱스 넘버 순서대로 1~9까지 지정해줌
        
        if data_yonsei['Units'].iloc[t_yonsei] == 'Nanograms per cubic meter (ng/m3)':
            data_yonsei['Units'].iloc[t_yonsei] = 'Micrograms per cubic meter (ug/m3)'
            data_yonsei['Value'].iloc[t_yonsei] = data_yonsei['Value'].iloc[t_yonsei]/1000
       
#%%        
###################날짜세팅(의미없음)######
for i_yonsei in range (0,np.size(data_yonsei.index)):
    data_yonsei['date'].iloc[i_yonsei] = str(data_yonsei['Start_Year_local'].iloc[i_yonsei])+'-'+str(format(data_yonsei\
                                                                                                            ['Start_Month_local'].iloc[i_yonsei],'02'))+'-'+str(format(data_yonsei\
                                                                                                                                                                ['Start_Day_local'].iloc[i_yonsei],'02'))

##################sort 정렬##############
data_yonsei = data_yonsei.sort_values(by=['Filter_ID','index_number'] ,ascending=True) #필터번호와 파라미터 인덱스로 정렬
data_yonsei = data_yonsei.reset_index(drop=True)

#%%
# # ## 9 = max_size

for j_yonsei in range (0, np.size(filter_id_yonsei)):
    globals()['period'+str(j_yonsei)] = pd.DataFrame([data_yonsei['Value'][max_size_yonsei*j_yonsei+0:max_size_yonsei*j_yonsei+max_size_yonsei]]) #9개씩 끊어서 나눔
    globals()['period'+str(j_yonsei)].columns = [data_yonsei['Parameter_Name'][max_size_yonsei*j_yonsei+0:max_size_yonsei*j_yonsei+max_size_yonsei]]
        
    f_list_yonsei.append(globals()['period'+str(j_yonsei)]) #필터수만큼의 풀 데이터프레임 각각 제작
    
#날짜리스트    
day_list_yonsei = np.unique(data_yonsei.date)
day_list_yonsei = pd.to_datetime(day_list_yonsei)

#병합
f_yonsei = np.vstack(f_list_yonsei)
f_yonsei = pd.DataFrame(f_yonsei)
f_yonsei.columns = parameter_name_list_yonsei
f_yonsei.index = pd.DatetimeIndex(day_list_yonsei)
f_yonsei['filter_name'] = filter_id_yonsei

#%%
######## 그냥 원래라면 있었어야 할 필터이름들 전부. (의미없음)
filter_name_yonsei = list(range (1, round(math.ceil(int(filter_id_yonsei[-1].split('-')[1])),-1)+1)) #1부터 필터아이디 맨 마지막 번호로 10의자리 만들어서 토탈 필터번호 제작

for fil_yonsei in range(0,np.size(filter_name_yonsei)):
    filter_name_yonsei[fil_yonsei] = 'KRSE-'+str(format(filter_name_yonsei[fil_yonsei],'04'))

filter_name_yonsei = pd.DataFrame(filter_name_yonsei)
filter_name_yonsei.columns = ['filter_name']

#%%


#%%

spartan_unist = path+'FilterBased_ReconstrPM25_KRUL.csv'


#%%################기초 데이터 생성####################################
data_org_unist = pd.read_table(spartan_unist,sep=",", skiprows=1)#,usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,\
data_unist = data_org_unist.copy()                                   # 17,18,19,20,21,22,23,24])

#%%##############필터 별 정렬 위해서 새로운 인덱스 만들기###################
data_unist['index_number'] = np.nan
data_unist['start_end_time'] = np.nan
data_unist['date'] = np.nan

f_list_unist = []

#%%
filter_id_unist = np.unique(data_org_unist.Filter_ID) #필터 각각 번호
id_size_unist = np.size(filter_id_unist) #필터 총 개수


grouped_unist = data_org_unist.groupby('Filter_ID')
max_size_unist = np.max(grouped_unist.size()) # 필터별 파라미터 최대 개수, 아마도 9
################Search full df################
for filter_s_unist in filter_id_unist:                          #필터 1번부터 끝까지
    search_s_unist = data_unist[data_unist['Filter_ID']==filter_s_unist]    #필터아이디 같은거끼리 모음 = 각 필터별의 데이터 bc, sulfate 등등
    if np.shape(search_s_unist)[0] == max_size_unist:           #파라미터 수가 max와 같으면
        full_df_unist = search_s_unist.copy()                   #처음으로 max인 필터의 데이터 모두 저장
        break
#%%
for filter_n_unist in filter_id_unist:   #필터 1번부터 끝까지
    print(filter_n_unist)
    search_unist = data_unist[data_unist['Filter_ID']==filter_n_unist]
    if np.shape(search_unist)[0] == max_size_unist:             #파라미터 개수 풀이면 넘어감
        continue
    else:
        full_df_search_unist = full_df_unist.copy()             #파라미터 개수 부족하면 

        for k_unist in range(0,np.shape(search_unist)[0]):      #파라미터 개수 부족한 그 데이터에서 
            search_product_unist = search_unist.Parameter_Code.iloc[k_unist] #각각 파라미터 하나씩 읽음
            exist_index_unist = full_df_search_unist[full_df_search_unist.Parameter_Code == search_product_unist].index[0] #읽은 파라미터의 원래 인덱스번호
            full_df_search_unist = full_df_search_unist.drop(exist_index_unist) #얘들이 존재하는 인덱스 번호를 풀 df에서 제거함
            
        full_df_search_unist.Filter_ID = filter_n_unist #존재 안하는 파라미터 줄만 뽑아서 필터이름 동일하게 설정하고 데이터는 없게함.
        full_df_search_unist.Value=np.nan
        
        data_unist = data_unist.append(full_df_search_unist) #새로 만들어진 보충용 파라미터 추가함! 따라서 데이터 수는 총 9xfilter id개수

#%%
parameter_list_unist = pd.DataFrame(full_df_unist.Parameter_Code).reset_index().Parameter_Code
parameter_name_list_unist = pd.DataFrame(full_df_unist.Parameter_Name).reset_index().Parameter_Name

for t_unist in range (0, np.size(data_unist.index)):
    for h_unist in range (0, np.size(parameter_list_unist)):

        if data_unist['Parameter_Code'].iloc[t_unist] == parameter_list_unist[h_unist] :#Filter PM2.5 mass
            data_unist['index_number'].iloc[t_unist] = parameter_list_unist.index[h_unist] #인덱스 넘버 순서대로 1~9까지 지정해줌
        
        if data_unist['Units'].iloc[t_unist] == 'Nanograms per cubic meter (ng/m3)':
            data_unist['Units'].iloc[t_unist] = 'Micrograms per cubic meter (ug/m3)'
            data_unist['Value'].iloc[t_unist] = data_unist['Value'].iloc[t_unist]/1000
       
#%%        
###################날짜세팅(의미없음)######
for i_unist in range (0,np.size(data_unist.index)):
    data_unist['date'].iloc[i_unist] = str(data_unist['Start_Year_local'].iloc[i_unist])+'-'+str(format(data_unist\
                                                                                                            ['Start_Month_local'].iloc[i_unist],'02'))+'-'+str(format(data_unist\
                                                                                                                                                                ['Start_Day_local'].iloc[i_unist],'02'))

##################sort 정렬##############
data_unist = data_unist.sort_values(by=['Filter_ID','index_number'] ,ascending=True) #필터번호와 파라미터 인덱스로 정렬
data_unist = data_unist.reset_index(drop=True)

#%%
# # ## 9 = max_size

for j_unist in range (0, np.size(filter_id_unist)):
    globals()['period'+str(j_unist)] = pd.DataFrame([data_unist['Value'][max_size_unist*j_unist+0:max_size_unist*j_unist+max_size_unist]]) #9개씩 끊어서 나눔
    globals()['period'+str(j_unist)].columns = [data_unist['Parameter_Name'][max_size_unist*j_unist+0:max_size_unist*j_unist+max_size_unist]]
        
    f_list_unist.append(globals()['period'+str(j_unist)]) #필터수만큼의 풀 데이터프레임 각각 제작
    
#날짜리스트    
day_list_unist = np.unique(data_unist.date)
day_list_unist = pd.to_datetime(day_list_unist)

#병합
f_unist = np.vstack(f_list_unist)
f_unist = pd.DataFrame(f_unist)
f_unist.columns = parameter_name_list_unist
f_unist.index = pd.DatetimeIndex(day_list_unist)
f_unist['filter_name'] = filter_id_unist

#%%
######## 그냥 원래라면 있었어야 할 필터이름들 전부. (의미없음)
filter_name_unist = list(range (1, round(math.ceil(int(filter_id_unist[-1].split('-')[1])),-1)+1)) #1부터 필터아이디 맨 마지막 번호로 10의자리 만들어서 토탈 필터번호 제작

for fil_unist in range(0,np.size(filter_name_unist)):
    filter_name_unist[fil_unist] = 'KRSE-'+str(format(filter_name_unist[fil_unist],'04'))

filter_name_unist = pd.DataFrame(filter_name_unist)
filter_name_unist.columns = ['filter_name']

#%%



#%%%

f_yonsei = f_yonsei.dropna(thresh = 4)
f_unist = f_unist.dropna(thresh = 4)

#%%

sum_yonsei = f_yonsei.sum()
sum_unist = f_unist.sum()

#%%
label = list(f_yonsei.columns[1:8])
color = ['pink','gold','skyblue','brown','grey','green','lightgrey']

#%%
plt.subplots(figsize=(14,8))
ax1 = plt.subplot(1,2,1)
plt.pie([sum_yonsei[1],sum_yonsei[2],sum_yonsei[3],sum_yonsei[4],sum_yonsei[5]]\
        ,labels=None, autopct='%.1f%%', colors=color)
plt.title('Yonsei University', fontsize=15,fontweight='bold')
plt.text(-0.7,-1.5,str(f_yonsei.index[0]).split(' ')[0]+' ~ '+str(f_yonsei.index[-1]).split(' ')[0]\
          ,fontsize=15, fontweight='bold')
#%%
ax2 = plt.subplot(1,2,2)
pie = ax2.pie([sum_unist[1],sum_unist[2],sum_unist[3],sum_unist[4],sum_unist[5]]\
        ,labels=None, autopct='%.1f%%', colors=color)
plt.legend(pie[0],label,loc=(1,0.4), fontsize=11) 
plt.title('UNIST', fontsize=15, fontweight='bold')
plt.text(-0.7,-1.5,str(f_unist.index[0]).split(' ')[0]+' ~ '+str(f_unist.index[-1]).split(' ')[0]\
          ,fontsize=15, fontweight='bold')


plt.suptitle('Total fraction by type',fontsize=20, fontweight='bold')
plt.savefig('Yonsei_Unist_total_type.png', dpi=500, bbox_inches='tight')
