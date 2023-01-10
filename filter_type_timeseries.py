import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('mode.chained_assignment',  None) # 경고 off


![image](https://user-images.githubusercontent.com/121787538/211461732-bb5561af-a1f8-46c8-a326-fb95e8ff2326.png)

#%%

path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/FilterBased_ReconstrPM25_KRUL (9).csv'
# path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/FilterBased_ReconstrPM25_KRSE (6).csv'

# path = '/Users/eomsujin/OneDrive - UNIST/SPARTAN/FilterBased_ReconstrPM25_KRUL (7).csv'

data_org = pd.read_table(path,sep=",", skiprows=1)
data = data_org.copy()



data['index_number'] = np.nan
data['start_end_time'] = np.nan
data['date'] = np.nan
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
    # elif data['Parameter_Code'].iloc[i]==28401:#Ammoniated Sulfate
    #     data['index_number'].iloc[i] = 2
        
    # elif data['Parameter_Code'].iloc[i]==28402:#Ammonium Nitrate
    #     data['index_number'].iloc[i] = 3
        
    # elif data['Parameter_Code'].iloc[i]==28802:#Sea Salt
    #     data['index_number'].iloc[i] = 4
        
    # elif data['Parameter_Code'].iloc[i]==28305:#Fine Soil
    #     data['index_number'].iloc[i] = 5
        
    # elif data['Parameter_Code'].iloc[i]==28201:#Equivalent BC PM2.5
    #     data['index_number'].iloc[i] = 6
        
    # elif data['Parameter_Code'].iloc[i]==28307:#Trace Element Oxides
    #     data['index_number'].iloc[i] = 7
    #     data['Value'].iloc[i] = data['Value'].iloc[i]/1000
    #     data['Units'].iloc[i] = 'Micrograms per cubic meter (ug/m3)'
        
    # elif data['Parameter_Code'].iloc[i]==28306:#Residual Matter
    #     data['index_number'].iloc[i] = 8

    # elif data['Parameter_Code'].iloc[i]==18301:#kappa
    #     data['index_number'].iloc[i] = 9
        
for i in range (0,np.size(data.index)):
    data['date'].iloc[i] = str(data['Start_Year_local'].iloc[i])+'-'+str(format(data['Start_Month_local'].iloc[i],'02'))+'-'+str(format(data['Start_Day_local'].iloc[i],'02'))



data = data.sort_values(by=['Filter_ID','index_number'] ,ascending=True)
data = data.reset_index(drop=True)

# ## 9 = max_size

for j in range (0, np.size(filter_id)):
    globals()['period'+str(j)] = pd.DataFrame([data['Value'][max_size*j+0:max_size*j+max_size]])
    globals()['period'+str(j)].columns = [data['Parameter_Name'][max_size*j+0:max_size*j+max_size]]
    
    
    f_list.append(globals()['period'+str(j)])
    
day_list = np.unique(data.date)
    
f = np.vstack(f_list)
f = pd.DataFrame(f)
f.columns = parameter_name_list
f.index = pd.DatetimeIndex(day_list)


#%%

plt.subplots(figsize = (10,8))

#Filter PM2.5 mass
# plt.plot(f['Filter PM2.5 mass'],color='black', linewidth=0.8, linestyle='--', label=f.columns[0], marker='o' ) 
#Ammoniated Sulfate
plt.plot(f[f.columns[1]],color='pink', linewidth=0.8, linestyle='--', label=f.columns[1], marker='o' )

#Ammonium Nitrate   
plt.plot(f[f.columns[2]],color='gold', linewidth=0.8, linestyle='--', label=f.columns[2], marker='^' )

#Sea Salt
plt.plot(f[f.columns[3]],color='skyblue', linewidth=0.8, linestyle='--', label=f.columns[3], marker='o' )

#Fine Soil  
plt.plot(f[f.columns[4]],color='brown', linewidth=0.8, linestyle='--', label=f.columns[4], marker='^' )

#Equivalent BC PM2.5 
plt.plot(f[f.columns[5]],color='grey', linewidth=0.8, linestyle='--', label=f.columns[5], marker='o' )

#Trace Element Oxides   
plt.plot(f[f.columns[6]],color='green', linewidth=0.8, linestyle='--', label=f.columns[6], marker='^' )

#Residual Matter   
# plt.plot(f[f.columns[7]],color='purple', linewidth=0.8, linestyle='--', label=f.columns[7], marker='o' ) 

#kappa  
# plt.plot(f[f.columns[8]],color='black', linewidth=0.8, linestyle='--', label=f.columns[8], marker='o', markersize='')   

plt.ylim([0,15])
plt.xticks(rotation=45)
# plt.xlabel('date', fontsize=15)
plt.ylabel('concentration (ug/m3)', fontsize=15)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
# plt.xlim((f.index[16],f.index[49]))

plt.title('PM2.5 filter based recons UNIST')
plt.savefig('filter_type_unist.png', dpi=500, bbox_inches='tight')
