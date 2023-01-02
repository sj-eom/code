import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import math
import glob
from matplotlib.colors import ListedColormap
pd.set_option('mode.chained_assignment',  None) # 경고 off
#%%

site = 'aeronet_seoul'
site = 'aeronet_yonsei'

path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/'
# path = '/Users/eomsujin/OneDrive - UNIST/SPARTAN/'

#%%
aeronet = glob.glob(path+site+'/'+'*'+'full_parameter.csv')[0]
spartan_25 = path+'FilterBased_ReconstrPM25_KRSE.csv'

#%%################기초 데이터 생성####################################
data_org = pd.read_table(spartan_25,sep=",", skiprows=1)#,usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,\
data = data_org.copy()                                   # 17,18,19,20,21,22,23,24])

data_aeronet = pd.read_table(aeronet,sep=",")
data_aeronet['times'] = pd.to_datetime(data_aeronet['times'])
data_aeronet = data_aeronet.set_index('times')

data_siz = data_aeronet[data_aeronet.columns[20:42]]

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
data_siz['sum'] = data_siz.iloc[:,:].sum(axis=1)

#%%
#9일평균 하기위함
aod440 = pd.DataFrame(data_aeronet['AOD_440nm']) ## 440 AOD~~
aod550 = pd.DataFrame(data_aeronet['AOD_550'])
fmf = pd.DataFrame(data_aeronet['FMF_550'])
ssa440 = pd.DataFrame(data_aeronet['SSA_440'])
ssa675 = pd.DataFrame(data_aeronet['SSA_675'])
ssa870 = pd.DataFrame(data_aeronet['SSA_870'])
ssa1020 = pd.DataFrame(data_aeronet['SSA_1020'])

aae = pd.DataFrame(data_aeronet['AAE'])
sae = pd.DataFrame(data_aeronet['SAE'])
eae = pd.DataFrame(data_aeronet['EAE'])
dep = pd.DataFrame(data_aeronet['Depolarization_Ratio[440nm]'])
lid = pd.DataFrame(data_aeronet['Lidar_Ratio[440nm]'])
siz = data_siz #ratio

siz = siz.drop([siz.columns[-1]],axis=1)
nor_siz = siz.copy()

total = aod440.join(aod550).join(fmf).join(ssa440).join(ssa675).join(ssa870).join(ssa1020).join(aae).join(sae).join(eae).join(dep).join(lid).join(siz)
###total = 단순히 1월 1일부터 모든 에어로넷 데이터모음###

#%%
########size distribution 노말라이징하기#################
for k in range (0, np.size(nor_siz.index)):
    bin_list = []
    real_bin = []
    for ii in range (0, np.size(nor_siz.columns)): #####normalized
        nor_siz[nor_siz.columns[ii]][k] = nor_siz[nor_siz.columns[ii]][k]/data_siz['sum'][k]

        bin_list.append('data_'+str(nor_siz.columns[ii]).split('.')[1])
        real_bin.append(nor_siz.columns[ii])
        
#%%
###### day_total = 샘플링 기간에만 해당하는 모든 기간 일 데이터#####
day_total = []

for d in day_list:
    for p in range (0, np.size(total.index)):
        if total.index[p]== d:

            day_total.append(total[p:p+9]) #샘플기간 조심하기..!

day_total = pd.concat(day_total)
day_total.columns = ['aod440','aod550', 'fmf', 'ssa440','ssa675','ssa870','ssa1020', 'aae', 'sae','eae', 'dep','lid']+bin_list
day_total.index.name = 'times'

#%%
##### day9_total = 샘플링기간에만 해당하는 데이터 9일씩 평균함 (siz의 경우 normalize된 값을 평균함)
aeronet_parameter = ['aod440','aod550', 'fmf', 'ssa440','ssa675','ssa870', 'aae', 'sae', 'eae','dep','lid','nor_siz']
day9_total = pd.DataFrame()

for par in aeronet_parameter:
    globals()['day9_'+str(par)] = []
    
    for da in range (0, np.size(day_list)): #샘플링기간만 9일씩 가져온 뒤에 9일평균함
        globals()['day9_'+str(par)].append(globals()[par].loc[str(day_list[da]):str(day_list[da] + timedelta(days = 8))].mean())
    
    globals()['day9_'+str(par)] = pd.DataFrame(globals()['day9_'+str(par)]) #9일평균 파라미터> 데이터프레임화
    day9_total = pd.concat([day9_total,globals()['day9_'+str(par)]],axis=1) #파라미터별로 9일평균된걸 옆으로 합치기

day9_total.columns = ['aod440','aod550', 'fmf', 'ssa440','ssa675','ssa870', 'aae', 'sae', 'eae','dep','lid']+bin_list
day9_total.index = day_list  ###day9total = ""noramlized된거 9일평균함""

#%%
##### f = 스파르탄 데이터 
f.index.name = 'times'

time_index = pd.date_range(start = day_list[0], end = day_list[-1]+ timedelta(days = 8), freq='1d', name='times')
time_index = pd.DataFrame(time_index) #샘플링 기간에 대해서만 데이인덱스 만들기

nan_data = pd.merge(time_index, day_total, how='outer', on='times')
nan_data = pd.merge(nan_data, f, how='outer', on='times')
nan_data = nan_data.set_index(['times'],drop=True) 
###샘플링 기간에 대해서 에어로넷 "일데이터" ""normalize 안 된 size dis"" + 스파르탄 데이터 합치기

#%%
real_name = nan_data.copy()

for l in range (0, len(real_bin)):
    real_name.rename(columns = {real_name.columns[l+11]: real_bin[l]}, inplace=True) 
### size distribution 칼럼이름 다시 되돌리기

#%%

### 샘플링기간만에 대해서 에어로넷 모든 데이터+일반size dis+스파르탄 데이터+normed size dis
summarize = real_name.join(nor_siz.add_prefix('x_'))

###### 9일 평균데이터에 스파르탄 데이터 붙임#####
day9_total = day9_total.join(summarize[summarize.columns[34:44]])


#%%
'''
real_bin = ['0.050000', '0.065604', '0.086077', '0.112939', '0.148184', '0.194429', '0.255105',
  '0.334716', '0.439173', '0.576227', '0.756052', '0.991996', '1.301571', '1.707757', '2.240702',
  '2.939966', '3.857452', '5.061260', '6.640745', '8.713145', '11.432287', '15.000000']
'''

figure_order = ['Filter PM2.5 mass','Ammoniated Sulfate', 'Ammonium Nitrate', 'Sea Salt', 'Fine Soil', 'Equivalent BC PM2.5']

#%%
#케미칼 데이터 nan값 0으로 처리
day9_total[day9_total.columns[34:41]] = day9_total[day9_total.columns[34:41]].fillna(0)

#음수 처리
day9_total['Ammoniated Sulfate'][day9_total['Ammoniated Sulfate']<0]=0


for day in day_list:
    for daily in range (0,np.size(summarize.index)):      
        if summarize.index[daily] == day:
            l = plt.figure(figsize=(44,8)) 
            
            for fin in range (0,9):
                
                real_day = summarize.index[daily+fin]
                
                if summarize.index[daily+fin] == real_day :
                    
                    ######매일 매일의 siz dis######
                    plt.subplot(2,11,fin+1)
                    plt.plot(real_bin,summarize[summarize.columns[12:34]][daily+fin:daily+fin+1].iloc[0], color='blue', marker='.')
                    plt.title(str(real_day).split(' ')[0])
                    plt.ylim(0,0.202441)
                    plt.xticks(rotation=45, fontsize=5)
                    if np.isnan(summarize.aod440[daily+fin])== False:
                        plt.text(0.13,0.18,'AOD='+str(round(summarize.aod440[daily+fin],3)), fontsize=12)
                        plt.text(0.13,0.168,'FMF='+str(round(summarize.fmf[daily+fin],3)), fontsize=12)
                        plt.text(0.13,0.156,'SSA='+str(round(summarize.ssa440[daily+fin],3)), fontsize=12)
                        ###반올림으로 바꾸기
                    
                    ##### FMF-SSA relation #####
                    plt.subplot(2,11,21) 
                    # plt.plot(summarize[summarize.columns[2]].loc[day:day+timedelta(days=8)],\
                    #          summarize[summarize.columns[3]].loc[day:day+timedelta(days=8)], \
                    #              color='black',alpha=0.5, marker='o', linestyle='')
                    # plt.xlim(0,1)
                    # plt.xlabel('FMF550')
                    # plt.ylim(0.85,1)
                    # plt.ylabel('SSA440')

                    plt.scatter(summarize.eae.loc[day:day+timedelta(days=8)],\
                             summarize.ssa440.loc[day:day+timedelta(days=8)],c=summarize.fmf.loc[day:day+timedelta(days=8)],marker='o', \
                                  cmap='jet')
                    plt.colorbar()
                    plt.clim(0,1)
                    plt.xlabel('EAE')
                    plt.ylabel('SSA')
                    plt.xlim(0,2.5)
                    plt.ylim(0.85,1)

                    
                    
                    ##### 파장별 SSA #####
                    plt.subplot(2,11,11+fin+1)
                    plt.plot([440,675,870,1020],summarize[summarize.columns[3:7]][daily+fin:daily+fin+1].iloc[0], color='black', marker='.', linestyle='--')
                    plt.title('SSA')
                    plt.ylim(0.85,1.0)
                    plt.xlim(400,1040)
                    plt.xticks([440,675,870,1020],['440nm','675nm','870nm','1020nm'],rotation=45, fontsize=10)
                    
                    ##### norm siz dis #####
                    plt.subplot(2,11,10) #norm된 siz dis 모두 나타내고 평균하기
                    plt.plot(real_bin,summarize[summarize.columns[44:66]][daily+fin:daily+fin+1].iloc[0], color='grey',alpha=0.5, marker='')
                    for mean_siz in range (0, np.size(day9_total.index)):
                        if real_day == day9_total.index[mean_siz]:
                            plt.plot(real_bin,day9_total[day9_total.columns[11:33]][mean_siz:mean_siz+1].iloc[0], color='black', marker='')
                            
                            
                            if np.isnan(day9_total.aod440[mean_siz])== False:
                                ########9일평균 파라미터#######################
                                plt.text(0.13,0.18,'AOD='+str(round(day9_total.aod440[mean_siz],3)), fontsize=12)
                                plt.text(0.13,0.168,'FMF='+str(round(day9_total.fmf[mean_siz],3)), fontsize=12)
                                plt.text(0.13,0.156,'SSA='+str(round(day9_total.ssa440[mean_siz],3)), fontsize=12)
                                plt.title('normalized(ratio) siz-dis') ### norm 평균도 같이 나타내보기?
                                plt.ylim(0,0.202441)
                                plt.xticks(rotation=45, fontsize=5)


                    
                    #####major chemical차트#####
                    plt.subplot(2,11,11) 
                    for pie_num in range (0, np.size(day9_total.index)):
                        if real_day == day9_total.index[pie_num]:
                            if day9_total['Ammoniated Sulfate'][pie_num]+\
                            day9_total['Ammonium Nitrate'][pie_num]+\
                            day9_total['Sea Salt'][pie_num]+\
                            day9_total['Fine Soil'][pie_num]+\
                            day9_total['Equivalent BC PM2.5'][pie_num] >0:
    
                                plt.pie([day9_total['Ammoniated Sulfate'][pie_num],
                                          day9_total['Ammonium Nitrate'][pie_num], \
                                              day9_total['Sea Salt'][pie_num]\
                                              , day9_total['Fine Soil'][pie_num], \
                                                  day9_total['Equivalent BC PM2.5'][pie_num]],\
                                        labels=['Sulfate','Nitrate', 'Sea Salt', 'Soil', 'BC'],\
                                            colors=['pink','yellow','skyblue','brown','grey'])
                                    
                            
                    #####pm concentration 차트#####
                    plt.subplot(2,11,22) 
                    plt.bar([0,1],[day9_total['Filter PM2.5 mass'].loc[day],day9_total['Ammoniated Sulfate'].loc[day]+\
                                    day9_total['Ammonium Nitrate'].loc[day]+day9_total['Sea Salt'].loc[day]+\
                                        day9_total['Fine Soil'].loc[day]+day9_total['Equivalent BC PM2.5'].loc[day]], \
                            color=['b','r'], alpha=0.2)
                    plt.ylim(0,80)
                    plt.xticks([0,1],['total','Major chem'])
                    plt.title('PM2.5 concentration')       
                    
                    
                    plt.suptitle('<'+str(day).split(' ')[0]+' '+site.split('_')[1]+'>',fontsize=20, fontweight = 'bold', ha='center')

            # plt.show()
            plt.savefig(path+site+'/'+site+'_'+str(day).split(' ')[0]+'.png', dpi=500, bbox_inches='tight')




