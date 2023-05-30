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
pd.set_option('mode.chained_assignment',  None) # 경고 off
#%%

site = 'aeronet_seoul'
site = 'aeronet_yonsei'
site = 'aeronet_unist'

path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/'
# path = '/Users/eomsujin/OneDrive - UNIST/SPARTAN/'

#%%
aeronet = glob.glob(path+site+'/'+'*'+'new_parameter.csv')[0]
spartan_25 = path+'FilterBased_ReconstrPM25_KRUL (10).csv'

#%%################기초 데이터 생성####################################
data_org = pd.read_table(spartan_25,sep=",", skiprows=1)#,usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,\
data = data_org.copy()                                   # 17,18,19,20,21,22,23,24])

data_aeronet = pd.read_table(aeronet,sep=",")
data_aeronet['times'] = pd.to_datetime(data_aeronet['times'])
data_aeronet = data_aeronet.set_index('times')
data_siz = data_aeronet[data_aeronet.columns[22:44]]

#%%##############필터 별 정렬 위해서 새로운 인덱스 만들기###################
data['index_number'] = np.nan
data['start_end_time'] = np.nan
data['date'] = np.nan

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

#병합
f = np.vstack(f_list)
f = pd.DataFrame(f)
f.columns = parameter_name_list
f.index = pd.DatetimeIndex(day_list)
f['filter_name'] = filter_id

#%%
######## 그냥 원래라면 있었어야 할 필터이름들 전부. (의미없음)
filter_name = list(range (1, round(math.ceil(int(filter_id[-1].split('-')[1])),-1)+1)) #1부터 필터아이디 맨 마지막 번호로 10의자리 만들어서 토탈 필터번호 제작

for fil in range(0,np.size(filter_name)):
    filter_name[fil] = 'KRSE-'+str(format(filter_name[fil],'04'))
filter_name = pd.DataFrame(filter_name)
filter_name.columns = ['filter_name']

#%%
########size distribution 노말라이징하기#################
data_siz['sum'] = data_siz.iloc[:,:].sum(axis=1)
siz = data_siz #ratio
siz = siz.drop([siz.columns[-1]],axis=1)
nor_siz = siz.copy()

for k in range (0, np.size(nor_siz.index)):
    bin_list = []
    real_bin = []
    for ii in range (0, np.size(nor_siz.columns)): #####normalized
        nor_siz[nor_siz.columns[ii]][k] = nor_siz[nor_siz.columns[ii]][k]/data_siz['sum'][k]

        bin_list.append('data_'+str(nor_siz.columns[ii]).split('.')[1])
        real_bin.append(nor_siz.columns[ii])


#%%
siz_labels = ['','','','','','','','','','','','','','','','','','','','','','',]

a_list = []

for a in range (len(day_list)):
    globals()['period_'+str(a)] = data_aeronet.loc[day_list[a]:day_list[a]+timedelta(days =8)]
    #에어로넷 자료 9일씩 끊기# 
    globals()['period_'+str(a)]['lee_type'] = np.nan
    globals()['period_'+str(a)]['eom_type'] = np.nan
    globals()['period_'+str(a)]['piyush_type'] = np.nan
    #데이터 타입 변경하기#
    globals()['period_'+str(a)] = globals()['period_'+str(a)].astype({'lee_type':'object'})
    globals()['period_'+str(a)] = globals()['period_'+str(a)].astype({'eom_type':'object'})
    globals()['period_'+str(a)] = globals()['period_'+str(a)].astype({'piyush_type':'object'})
    a_list.append(globals()['period_'+str(a)].mean()) #필터수만큼의 풀 데이터프레임 각각 제작

#%%

base = period_16


fig8, ax8 = plt.subplots(figsize = (10,8))
for e in range (0, np.size(base.index)):
    if base['SSA_440'][e] > 0:
        image = ax8.scatter([440,675,870,1020],base[base.columns[10:14]].iloc[e]\
                 ,c=[base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e]]\
                     , cmap='jet',vmin=0.1,vmax=1.2,\
                 marker='o', s=50, zorder=2 )
        plt.plot([440,675,870,1020],base[base.columns[10:14]].iloc[e],linewidth=0.8, \
                 linestyle='--',color='grey',zorder=1)
    else:
        continue
plt.ylim(0.88,1)
fig8.colorbar(image,label='AOD500')
plt.xticks([440,675,870,1020],rotation=45)
plt.title(str(base.index[0]).split(' ')[0]+'~'+str(base.index[-1]).split(' ')[0])

#%%
fig9, ax9 = plt.subplots(figsize = (10,8))
for e in range (0, np.size(base.index)):
    
    image2 = ax9.scatter(base.columns[22:44],base[base.columns[22:44]].iloc[e]\
             ,c=[base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],
                 base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],
                 base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],
                 base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],
                 base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],base['AOD_500nm'][e],
                 base['AOD_500nm'][e],base['AOD_500nm'][e]]\
                 , cmap='jet',vmin=0.1,vmax=1.2,\
             marker='o', s=50, zorder=2 )
    plt.plot(base.columns[22:44],base[base.columns[22:44]].iloc[e],linewidth=0.8, \
             linestyle='--',color='grey',zorder=1)
plt.ylim(0,0.12)
fig9.colorbar(image2,label='AOD500')
plt.xticks(base.columns[22:44],rotation=45)
plt.title(str(base.index[0]).split(' ')[0]+'~'+str(base.index[-1]).split(' ')[0])

#%%
fig10, ax10 = plt.subplots(figsize = (10,8))
for e in range (0, np.size(base.index)):
    
    image3 = ax10.scatter(base['EAE'],base['SSA_440']\
             ,c=base['AOD_500nm']\
                 , cmap='jet',vmin=0.1,vmax=1.2, marker='o', s=50, zorder=2 )
plt.ylim(0.8,1)
fig10.colorbar(image3,label='AOD500')
plt.xlim(0,2.5)
plt.title(str(base.index[0]).split(' ')[0]+'~'+str(base.index[-1]).split(' ')[0])

#%%
ssa_list = []
ratio_list = []

fig11, ax11 = plt.subplots(figsize = (10,8))
for g in range (0, np.size(f.index)):
    if np.isnan(f['Residual Matter'][g]) == False and np.isnan(f['Ammoniated Sulfate'][g]) == False: #값이 nan이 아니라면
    
        image4 = ax11.scatter(globals()['period_'+str(g)]['SSA_1020'].mean(),\
                              (f['BC PM2.5'][g])/f[f.columns[1:6]].sum(axis=1)[g],\
                 c=globals()['period_'+str(g)]['AOD_500nm'].mean(), cmap='jet',vmin=0.1,vmax=1.2, marker='o', s=f[f.columns[0]][g]*10, zorder=2 )
        
        ssa_list.append(globals()['period_'+str(g)]['SSA_1020'].mean())
        ratio_list.append((f['BC PM2.5'][g])/f[f.columns[1:6]].sum(axis=1)[g])


ssa_list = np.ma.masked_invalid(ssa_list) #nan값 마스크처리
ratio_list = np.ma.masked_invalid(ratio_list)

plt.ylim(0,1)
fig11.colorbar(image4,label='AOD500')
plt.xlim(0.85,1) 
plt.text(0.86,0.9,'R='+str(round(np.ma.corrcoef(ssa_list,ratio_list)[0,1],3)), fontsize=30)
plt.title('SSA1020-bc fraction')


#%%
fmf_list = []
ratio_list = []

fig12, ax12 = plt.subplots(figsize = (10,8))
for g in range (0, np.size(f.index)):
    if np.isnan(f['Residual Matter'][g]) == False and np.isnan(f['Ammoniated Sulfate'][g]) == False: #값이 nan이 아니라면
    
        image5 = ax12.scatter(globals()['period_'+str(g)]['FMF_550'].mean(),\
                              (f['Fine Soil'][g]+f['BC PM2.5'][g])/f[f.columns[1:6]].sum(axis=1)[g],\
                 c=globals()['period_'+str(g)]['AOD_500nm'].mean(), cmap='jet',vmin=0.1,vmax=1.2, marker='o', s=f[f.columns[0]][g]*10, zorder=2 )
        
        fmf_list.append(globals()['period_'+str(g)]['FMF_550'].mean())
        ratio_list.append((f['Fine Soil'][g]+f['BC PM2.5'][g])/f[f.columns[1:6]].sum(axis=1)[g])


fmf_list = np.ma.masked_invalid(fmf_list) #nan값 마스크처리
ratio_list = np.ma.masked_invalid(ratio_list)

plt.ylim(0,1)
fig12.colorbar(image4,label='AOD500')
plt.xlim(0.6,1) 
plt.text(0.66,0.9,'R='+str(round(np.ma.corrcoef(fmf_list,ratio_list)[0,1],3)), fontsize=30)
plt.title('FMF-soil+bc fraction')
