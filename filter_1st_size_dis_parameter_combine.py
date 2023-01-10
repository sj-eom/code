'''2022.07.07 ~ 2022.07.08 Sujin Eom'''
'''2022.07.11 Sujin Eom'''

##1st chemical##size,fmf-ssa,aae-sae##
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import math
from matplotlib.colors import ListedColormap
#%%
pd.set_option('mode.chained_assignment',  None) # 경고 off

aeronet = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_yonsei/yonsei_aeronet+lid.csv'
aeronet_siz = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_yonsei/yonsei_aeronet+siz.csv'
# aeronet = '/Users/eomsujin/OneDrive - UNIST//SPARTAN/aeronet_yonsei/yonsei_aeronet.csv'

spartan_25 = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/FilterBased_ReconstrPM25_KRSE (6).csv'
# spartan_25 = '/Users/eomsujin/OneDrive - UNIST/SPARTAN/FilterBased_ReconstrPM25_KRSE.csv'
# nephelo_25 = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/TimeResPM25_DailyEstPM25_KRSE.csv'

data_org = pd.read_table(spartan_25,sep=",", skiprows=1,usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,\
                                                                 17,18,19,20,21,22,23,24])

# data_org = pd.read_table(spartan_25,sep=",", skiprows=1)
# data_nephelo = pd.read_table(nephelo_25, sep=",", skiprows=1)
data_aeronet = pd.read_table(aeronet,sep=",")
data_aeronet['times'] = pd.to_datetime(data_aeronet['times'])
data_aeronet = data_aeronet.set_index('times')

data_siz = pd.read_table(aeronet_siz,sep=",")
data_siz['times'] = pd.to_datetime(data_siz['times'])
data_siz = data_siz.set_index('times')

#%%
data = data_org.copy()


data['index_number'] = np.nan
data['start_end_time'] = np.nan
data['date'] = np.nan
# data_nephelo['date'] = np.nan

f_list = []
    
#%%
#missing = np.ones([1,np.shape(data)[1]])*np.nan
filter_id = np.unique(data_org.Filter_ID)
id_size = np.size(filter_id)


#filter_id_T = np.reshape(filter_id, [id_size,1])
grouped = data_org.groupby('Filter_ID')
max_size = np.max(grouped.size())
################Search full df################
for filter_s in filter_id:
    search_s = data[data['Filter_ID']==filter_s]
    if np.shape(search_s)[0] == max_size:
        full_df = search_s.copy()
        break
#%%
for filter_n in filter_id:
    print(filter_n)
    search = data[data['Filter_ID']==filter_n]
    if np.shape(search)[0] == max_size:
        continue
    else:
        full_df_search = full_df.copy()

        for k in range(0,np.shape(search)[0]):
            search_product = search.Parameter_Code.iloc[k]
            exist_index = full_df_search[full_df_search.Parameter_Code == search_product].index[0]
            full_df_search = full_df_search.drop(exist_index)
            
        full_df_search.Filter_ID = filter_n
        full_df_search.Value=np.nan
        
        data = data.append(full_df_search)

#%%
parameter_list = pd.DataFrame(full_df.Parameter_Code).reset_index().Parameter_Code
parameter_name_list = pd.DataFrame(full_df.Parameter_Name).reset_index().Parameter_Name

for t in range (0, np.size(data.index)):
    for h in range (0, np.size(parameter_list)):

        if data['Parameter_Code'].iloc[t] == parameter_list[h] :#Filter PM2.5 mass
            data['index_number'].iloc[t] = parameter_list.index[h]
        
        if data['Units'].iloc[t] == 'Nanograms per cubic meter (ng/m3)':
            
            data['Units'].iloc[t] = 'Micrograms per cubic meter (ug/m3)'
            data['Value'].iloc[t] = data['Value'].iloc[t]/1000
       
#%%        
       
for i in range (0,np.size(data.index)):
    data['date'].iloc[i] = str(data['Start_Year_local'].iloc[i])+'-'+str(format(data['Start_Month_local'].iloc[i],'02'))+'-'+str(format(data['Start_Day_local'].iloc[i],'02'))

# for n in range (0,np.size(data_nephelo.index)):
#     data_nephelo['date'].iloc[n] = str(data_nephelo['Year_local'].iloc[n])+'-'+str(format(data_nephelo['Month_local'].iloc[n],'02'))+'-'+str(format(data_nephelo['Day_local'].iloc[n],'02'))


data = data.sort_values(by=['Filter_ID','index_number'] ,ascending=True)
data = data.reset_index(drop=True)


#%%
# ## 9 = max_size

for j in range (0, np.size(filter_id)):
    globals()['period'+str(j)] = pd.DataFrame([data['Value'][max_size*j+0:max_size*j+max_size]])
    globals()['period'+str(j)].columns = [data['Parameter_Name'][max_size*j+0:max_size*j+max_size]]
    
    
    f_list.append(globals()['period'+str(j)])
    
day_list = np.unique(data.date)
day_list = pd.to_datetime(day_list)

f = np.vstack(f_list)
f = pd.DataFrame(f)
f.columns = parameter_name_list
f.index = pd.DatetimeIndex(day_list)
f['filter_name'] = filter_id

# data_nephelo['date'] = pd.to_datetime(data_nephelo['date'])
# data_nephelo = data_nephelo.set_index('date')

#%%

filter_name = list(range (1, round(math.ceil(int(filter_id[-1].split('-')[1])),-1)+1)) #1부터 필터아이디 맨 마지막 번호로 10의자리 만들어서 토탈 필터번호 제작

for fil in range(0,np.size(filter_name)):
    filter_name[fil] = 'KRSE-'+str(format(filter_name[fil],'04'))

filter_name = pd.DataFrame(filter_name)
filter_name.columns = ['filter_name']

#%% bin 별로 ratio 구하기
data_siz['sum'] = data_siz.iloc[:,:].sum(axis=1)

for k in range (0, np.size(data_siz.index)):
    bin_list = []
    real_bin = []
    for ii in range (0, np.size(data_siz.columns)-1):
        data_siz[data_siz.columns[ii]][k] = data_siz[data_siz.columns[ii]][k]/data_siz['sum'][k]

        bin_list.append('data_'+str(data_siz.columns[ii]).split('.')[1])
        real_bin.append(data_siz.columns[ii])

#%%


#9일평균 하기위함
aod440 = data_aeronet['AOD_440nm'] ## 440 AOD~~
aod550 = data_aeronet['AOD_550']
fmf = data_aeronet['FMF_550']
ssa = data_aeronet['SSA_440']
aae = data_aeronet['AAE']
sae = data_aeronet['SAE']
dep = data_aeronet['Depolarization_Ratio[440nm]']
lid = data_aeronet['Lidar_Ratio[440nm]']
siz = data_siz #ratio

siz = siz.drop([siz.columns[-1]],axis=1)
                
                
aeronet_parameter = ['aod440','aod550', 'fmf', 'ssa', 'aae', 'sae', 'dep','lid','siz']
day9_total = pd.DataFrame()

for p in aeronet_parameter:
    globals()['day9_'+str(p)] = []
    
    for d in range (0, np.size(day_list)):
        globals()['day9_'+str(p)].append(globals()[p].loc[str(day_list[d]):str(day_list[d] + timedelta(days = 8))].mean())
    
    globals()['day9_'+str(p)] = pd.DataFrame(globals()['day9_'+str(p)])
    day9_total = pd.concat([day9_total,globals()['day9_'+str(p)]],axis=1)
    
#%%    
day9_total.columns = ['aod440','aod550', 'fmf', 'ssa', 'aae', 'sae', 'dep','lid']+bin_list
day9_total.index = day_list
day9_total.index.name = 'times'
# data_nephelo.index.name = 'times'
f.index.name = 'times'

time_index = pd.date_range(start = day_list[0], end = day_list[-1], freq='1d', name='times')#periods=10, freq='M')
time_index = pd.DataFrame(time_index)

nan_data = pd.merge(time_index, day9_total, how='outer', on='times')
nan_data = pd.merge(nan_data, f, how='outer', on='times')
# nan_data = pd.merge(nan_data, data_nephelo['Value'], how='outer', on='times')
# nan_data = pd.merge(filter_name, nan_data, how='outer', on='filter_name')
nan_data = nan_data.set_index(['times'],drop=True)

####calculating percent
nan_data['percent_sulfate'] = nan_data['Ammoniated Sulfate']/nan_data['Filter PM2.5 mass']*100
nan_data['percent_nitrate'] = nan_data['Ammonium Nitrate']/nan_data['Filter PM2.5 mass']*100
nan_data['percent_seasalt'] = nan_data['Sea Salt']/nan_data['Filter PM2.5 mass']*100

nan_data['percent_soil'] = nan_data['Fine Soil']/nan_data['Filter PM2.5 mass']*100
nan_data['percent_BC'] = nan_data['BC PM2.5']/nan_data['Filter PM2.5 mass']*100
nan_data['percent_oxides'] = nan_data['Trace Element Oxides']/nan_data['Filter PM2.5 mass']*100
nan_data['ratio'] = nan_data['Fine Soil']/nan_data['Ammoniated Sulfate']

nan_data['major'] = nan_data['Ammoniated Sulfate']+nan_data['Ammonium Nitrate']+\
    nan_data['Sea Salt']+nan_data['Fine Soil']+nan_data['BC PM2.5'] #차이가 최대 0.02정도 - 반올림때문인것으로보임
    

# nan_data['major'] = nan_data['Filter PM2.5 mass']-nan_data['Trace Element Oxides']-nan_data['Residual Matter']


count_list = list(range(1,np.size(filter_name),8))



for count in count_list:
    for ii in range (0, np.size(filter_name)):
        if filter_name['filter_name'][ii] == 'KRSE-'+str(format(count+6,'04')) or \
            filter_name['filter_name'][ii] == 'KRSE-'+str(format(count+7,'04')):
            
            filter_name['filter_name'][ii] = np.nan
        else:
            continue
            
filter_name = filter_name.dropna()


#%%

#drawing line
for num in range (0, np.size(nan_data.index)): 
    if np.size(nan_data.index)>=num+9 :
        
        if pd.isna(nan_data['Filter PM2.5 mass'][num]) == False and pd.isna(nan_data['Filter PM2.5 mass'][num+9]) == False:
            nan_data = nan_data.drop(nan_data.index[num+1:num+9])



#%%



#%% 1등 타입 골라서 AE, fmf등과 나타내기


###케미칼마다 번호지정###
major = nan_data[nan_data.columns[31:36]]
major['number'] = np.nan
for u in range (0, np.size(major.index)):
    if major.idxmax(axis=1)[u] == 'Ammoniated Sulfate':
        major['number'][u] = 1
    if major.idxmax(axis=1)[u] == 'Ammonium Nitrate':
        major['number'][u] = 2
    if major.idxmax(axis=1)[u] == 'Sea Salt':
        major['number'][u] = 3
    if major.idxmax(axis=1)[u] == 'Fine Soil':
        major['number'][u] = 4
    if major.idxmax(axis=1)[u] == 'BC PM2.5':
        major['number'][u] = 5


size_dis = nan_data[nan_data.columns[8:30]]
final = pd.concat([major,size_dis],axis=1)

#%%




list_sulfate = []
list_nitrate = []
list_soil = []
list_bc = []
list_seasalt = []

mean_sulfate = []
mean_nitrate = []
mean_soil = []
mean_bc = []
mean_seasalt = []

###표시된 넘버 기준으로 리스트 각각 만듦###
for m in range (0, np.size(final.index)):
    if final['number'][m] == 1:
        list_sulfate.append(final[m:m+1])
    if final['number'][m] == 2:
        list_nitrate.append(final[m:m+1])
    if final['number'][m] == 3:
        list_seasalt.append(final[m:m+1])
    if final['number'][m] == 4:
        list_soil.append(final[m:m+1])
    if final['number'][m] == 5:
        list_bc.append(final[m:m+1])

type_list = ['sulfate','nitrate','seasalt','soil','bc']

###각각 넘버의 리스트(1등케미칼 리스트)를 평균###
for q in type_list:
    if len(globals()['list_'+q])>0:
        globals()['d_'+q] = pd.concat(globals()['list_'+q])
        globals()['mean_'+q].append(globals()['d_'+q][globals()['d_'+q].columns[6:28]].mean())
    else:
        globals()['d_'+q] = pd.DataFrame(globals()['list_'+q])


#%%
#설명
#각 날짜별로(사실9일평균-평균전에는 ratio로 나타냄) 1등인 케미칼 고름, 그날의 size distribution 과 케미칼 엮음 > 
#1등일때마다 모두 모아서 평균함

c = plt.figure(figsize=(10,8))
plt.plot(real_bin,mean_sulfate[0], color='pink', label='Ammoniated Sulfate', marker='.')
plt.plot(real_bin,mean_bc[0], color='grey', label='BC PM2.5', marker='.')
plt.plot(real_bin,mean_soil[0], color='brown', label='Fine Soil', marker='.')

#주로 숫자 적으므로..
if len(mean_nitrate)==0:
    plt.plot(real_bin,np.zeros((1,22))[0]*np.nan, color='gold', label='Ammonium Nitrate')
else:
    plt.plot(real_bin,mean_nitrate[0], color='gold', label='Ammonium Nitrate', marker='.')


if len(mean_seasalt)==0:
    plt.plot(real_bin,np.zeros((1,22))[0]*np.nan, color='skyblue', label='Sea Salt')
else:
    plt.plot(real_bin,mean_seasalt[0], color='skyblue', label='Sea Salt', marker='.')
    
plt.ylim(0,0.14)    
plt.xlabel('bin')
plt.ylabel('ratio')
plt.legend()
plt.xticks(rotation=45)
plt.title('1st size distribution Yonsei_University')       

#%%
y = plt.figure(figsize=(10,8))
cMap = ListedColormap(['pink', 'gold', 'skyblue','brown','grey'])
plt.scatter(nan_data['sae'], nan_data['aae'], c=major['number'],cmap=cMap, edgecolors='black',linewidth=0.3, s=100)
cbar = plt.colorbar(label='type')
plt.clim(0.5,5.5)
cbar.set_ticks([1,2,3,4,5])
cbar.set_ticklabels(['Sulfate','Nitrate','Sea Salt','Fine Soil','BC'])

plt.xlim(-2.5,2.51)
plt.xticks(np.arange(-2,2.51,0.5))
plt.ylim(0,3.5)
plt.yticks(np.arange(0,3.01,1))
plt.xlabel('SAE 440-870nm')
plt.ylabel('AAE 440-870nm')
plt.title('1st Chemical AAE-SAE')



e = plt.figure(figsize=(10,8))
plt.scatter(nan_data['fmf'], nan_data['ssa'], c=major['number'],cmap=cMap, edgecolors='black',linewidth=0.3, s=100)
cbar = plt.colorbar(label='type')
plt.clim(0.5,5.5)
cbar.set_ticks([1,2,3,4,5])
cbar.set_ticklabels(['Sulfate','Nitrate','Sea Salt','Fine Soil','BC'])

plt.xlim(0.4,1)
plt.xticks(np.arange(0.4,1,0.2))
plt.ylim(0.85,1)
plt.yticks(np.arange(0.85,1,0.05))
plt.xlabel('Fine mode fraction 550nm')
plt.ylabel('Single scattering albedo 440nm')
plt.title('1st Chemical SSA-FMF')


b = plt.figure(figsize=(10,8))
plt.scatter(nan_data['dep'], nan_data['lid'], c=major['number'],cmap=cMap, edgecolors='black',linewidth=0.3, s=100)
cbar = plt.colorbar(label='type')
plt.clim(0.5,5.5)
cbar.set_ticks([1,2,3,4,5])
cbar.set_ticklabels(['Sulfate','Nitrate','Sea Salt','Fine Soil','BC'])

plt.xlim(0,0.5)
plt.xticks(np.arange(0,0.51,0.05))
plt.ylim(0,130)
# plt.yticks(np.arange(0.85,1,0.05))
plt.xlabel('9-day linear depolarization ratio')
plt.ylabel('9-day lidar ratio')
plt.title('1st Chemical Lid-Dep')

#%%
a = plt.figure(figsize=(28,15))

figure_order = ['Filter PM2.5 mass','Ammoniated Sulfate', 'Ammonium Nitrate', 'Sea Salt', 'Fine Soil', 'BC PM2.5']




for f in range (0,6):
    nan_data[str(figure_order[f])+'_per_major'] = nan_data[str(figure_order[f])]/nan_data['major']*100
    
    for fin in range (0, np.size(nan_data.index)):
        
        if nan_data[str(figure_order[f])+'_per_major'][fin] < 5:
            nan_data[str(figure_order[f])+'_per_major'][fin] = np.nan
    
    plt.subplot(2,3,f+1)
    plt.scatter(nan_data['dep'],nan_data['lid'],c=nan_data[str(figure_order[f])+'_per_major'],cmap='Purples', edgecolors='black',linewidth=0.5)
    plt.xlim(0,0.5)
    plt.xticks(np.arange(0,0.51,0.05))
    plt.ylim(0,130)
    # plt.yticks(np.arange(0,3.01,1))
    plt.xlabel('9-day linear depolarization ratio')
    plt.ylabel('9-day lidar ratio')
    cbar = plt.colorbar(label='ratio')
    plt.clim(0,80)
    cbar.set_ticks([0,20,40,60,80])
    cbar.set_ticklabels(['0%','20%','40%','60%','80%'])

    plt.title(str(figure_order[f]),fontsize=20, fontweight = 'bold')
    
    

plt.suptitle('chemical/major with lid-dep',fontsize=20, fontweight = 'bold', ha='center')
#%%
#440nm dep, lid
f = plt.figure(figsize=(10,8))
plt.xlim(0,0.5)
plt.xlabel('9-day linear depolarization ratio')
plt.ylabel('9-day lidar ratio')
plt.xticks(np.arange(0,0.51,0.05))
plt.ylim(0,130)
plt.plot(nan_data['dep'],nan_data['lid'],'o', color='grey')

