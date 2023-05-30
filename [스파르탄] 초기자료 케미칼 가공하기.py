'''chemical concat'''
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('mode.chained_assignment',  None) # 경고 off
# from iteration_utilities import unique_everseen, duplicates

#케미칼 타임시리즈#
#%%

path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/FilterBased_ChemSpecPM25_KRSE (7).csv'
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
# f.to_csv('C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_yonsei/spartan_yonsei_1_chemical.csv')
