'''2022.06.20 Sujin Eom'''
'''2022.11.03'''
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('mode.chained_assignment',  None) # 경고 off
# from iteration_utilities import unique_everseen, duplicates
#%%

path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/FilterBased_ChemSpecPM25_KRUL (5).csv'
# path = '/Users/eomsujin/OneDrive - UNIST/SPARTAN/FilterBased_ChemSpecPM25_KRSE.csv'

data_org = pd.read_table(path,sep=",", skiprows=1)
data = data_org.copy()



data['index_number'] = np.nan
data['start_end_time'] = np.nan
data['date'] = np.nan
f_list = []
    
#%%
filter_id = np.unique(data_org.Filter_ID)
id_size = np.size(filter_id)

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
        
        if data['Units'].iloc[t] == ' Nanograms per cubic meter (ng/m3)':
            data['Units'].iloc[t] = ' Micrograms per cubic meter (ug/m3)'
            data['Value'].iloc[t] = data['Value'].iloc[t]/1000
    
#%%
#sorting#
data = data.sort_values(by=['Filter_ID','index_number'] ,ascending=True)
data = data.reset_index(drop=True)


#max_size#
for j in range (0, np.size(filter_id)):
    globals()['period'+str(j)] = pd.DataFrame([data['Value'][max_size*j+0:max_size*j+max_size]])
    globals()['period'+str(j)].columns = [data['Parameter_Name'][max_size*j+0:max_size*j+max_size]]
    
    f_list.append(globals()['period'+str(j)])

#%%
#date#
for i in range (0,np.size(data.index)):
    data['date'].iloc[i] = str(data['Start_Year_local'].iloc[i])+'-'+str(format(data['Start_Month_local'].iloc[i],'02'))+'-'+str(format(data['Start_Day_local'].iloc[i],'02'))

#%%

day_list = np.unique(data.date)
f = np.vstack(f_list)
f = pd.DataFrame(f)
f.columns = parameter_name_list
f.index = pd.DatetimeIndex(day_list)

#%%

for n in range (0, np.size(f.columns)):
    if f[f.columns[n]].size > f[f.columns[n]].shape[0]: #size가 shape 보다 큰 경우 : 즉, 같은 이름의 열이 2개이상일경우!
        f[f.columns[n]] = f[f.columns[n]].mean(axis=1) # 두개 열을 평균한다

f = f.loc[:, ~f.T.duplicated()] # 중복된 열을 지운다

#%%



plt.subplots(figsize = (20,8))
color_map = ['#000000','#808080','#C0C0C0','#F3F355','#FF0000','#800000','#FFFF00','#808000','#00FF00','#008000','#00FFFF','#008080','#0000FF','#000080','#FF00FF','#800080','#E0709B','#E16350','#8A4C44','#8E6F80','#00B5E3','#5AC6D0','#00A6A9','#5DC19B','#6C71B5','#448CCB','#1C9249','#2E674E','#72C6A5','#5D3462','#403F95','#84A7D3','#006400','#FAEBD7','#FFE4E1','#ffa500','#0275d8']
for p in range (0, np.size(f.columns)-1):
    # if f.columns[p] == ' Filter PM2.5 mass':
    #     continue
    # else:
    plt.plot(f[f.columns[p+1]], color=color_map[p+1], linewidth=0.8, linestyle='--', label=f.columns[p+1], marker='o' )





plt.ylim([0,15])
plt.xticks(rotation=45)
plt.xlim(['2019-04-01'],['2022-12-01'])
# plt.xlabel('date', fontsize=15)
plt.ylabel('concentration (ug/m3)', fontsize=15)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1))

plt.title('PM2.5 chemical UNIST', fontsize=20)
