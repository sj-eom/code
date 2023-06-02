'''2023.05.30~06.02 Sujin'''
''' Making Class'''


#%%
import numpy as np
import pandas as pd
import glob
pd.set_option('mode.chained_assignment',  None) # 경고 off


#%% [Warning!] 사이트 이름 선택하기 / 자료 업데이트 될 경우 숫자 바꾸기
#site = unist, yonsei, seoul                                                   #seoul 선택할경우, 연대스파르탄+서울대에어로넷
class site:
    def __init__(self,site):
        if site == 'unist':
            self.inform = ['KRUL (13)', 'KRUL (7)','aeronet_unist','20200101_20221231_KORUS_UNIST_Ulsan'] 
                            #필터자료 번호 #이온자료 번호 #에어로넷 자료 폴더 #자료기간+모든파라미터 확보 필수
                            
        elif site == 'yonsei':
            self.inform = ['KRSE (11)', 'KRSE (9)','aeronet_yonsei','20190101_20221231_Yonsei_University'] 
                            #필터자료 번호 #이온자료 번호 #에어로넷 자료 폴더 #자료기간+모든파라미터 확보 필수

        elif site == 'seoul':
            self.inform = ['KRSE (11)', 'KRSE (9)','aeronet_seoul','20190101_20221231_Seoul_SNU'] 
 
        # a= self.ulsan[0]
        # b= self.ulsan[1]
site = site('unist')

#%% SPARTAN : 데이터프레임 생성하기  '파일이름'
def filter_station (file_name):
    
    path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/'
    spartan_25 = path+file_name #KRSE - 6 (12월), 7 (2월28) #KRUL - 9 (12월), 10(2월28)
    
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
    # id_size = np.size(filter_id) #필터 총 개수
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
    return f
df_filter = filter_station (f'FilterBased_ReconstrPM25_{site.inform[0]}.csv') #필터자료 정렬

#%% SPARTAN : 데이터프레임 생성하기 (chemical) '파일이름'
def filter_chemical (file_name):
    path = f'C:/Users/PC/OneDrive - UNIST/SPARTAN/{file_name}'
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
    return f
df_chemical = filter_chemical(f'FilterBased_ChemSpecPM25_{site.inform[1]}.csv') #필터 이온자료

#%% AERONET : 초기자료 불러오기  파일경로/폴더/기간_지점(정확히)
class Initial:
    def __init__(self, path):
        self.aod = pd.read_table(path+'.lev15',sep=",", skiprows=6)
        self.ssa = pd.read_table(path+'.ssa',sep=",", skiprows=6)
        self.fmf = pd.read_table(path+'.ONEILL_lev15',sep=",", skiprows=6)
        self.aae = pd.read_table(path+'.tab',sep=",", skiprows=6)
        self.eae = pd.read_table(path+'.aod',sep=",", skiprows=6)
        self.dep = pd.read_table(path+'.lid',sep=",", skiprows=6)
        self.siz = pd.read_table(path+'.siz',sep=",", skiprows=6)
Initial = Initial(f'C:/Users/PC/OneDrive - UNIST/SPARTAN/{site.inform[2]}/{site.inform[3]}')

# 울산은 2020년부터

#%% AERONET : Datetime 으로 인덱스 지정하기
class To_D_Index:
    def __init__(self):
        self.aod = Initial.aod.replace(to_replace = -999, value = np.nan)
        self.aod['times'] = pd.to_datetime(self.aod['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.aod = self.aod.set_index('times')
        
        self.fmf = Initial.fmf.replace(to_replace = -999, value = np.nan) #FMF만 Date 칼럼 이름이 다름 주의하기
        self.fmf['times'] = pd.to_datetime(self.fmf['Date_(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.fmf = self.fmf.set_index('times')        

        self.ssa = Initial.ssa.replace(to_replace = -999, value = np.nan)
        self.ssa['times'] = pd.to_datetime(self.ssa['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.ssa = self.ssa.set_index('times')

        self.aae = Initial.aae.replace(to_replace = -999, value = np.nan)
        self.aae['times'] = pd.to_datetime(self.aae['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.aae = self.aae.set_index('times')

        self.eae = Initial.eae.replace(to_replace = -999, value = np.nan)
        self.eae['times'] = pd.to_datetime(self.eae['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.eae = self.eae.set_index('times')

        self.dep = Initial.dep.replace(to_replace = -999, value = np.nan)
        self.dep['times'] = pd.to_datetime(self.dep['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.dep = self.dep.set_index('times')

        self.siz = Initial.siz.replace(to_replace = -999, value = np.nan)
        self.siz['times'] = pd.to_datetime(self.siz['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
        self.siz = self.siz.set_index('times')
To_D_Index = To_D_Index()

#%% AERONET : 필요한 칼럼만 추출하기
class Extract:
    def __init__(self):
        self.aod = To_D_Index.aod[['AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm','AOD_1020nm','Precipitable_Water(cm)','440-870_Angstrom_Exponent']]
        self.fmf = To_D_Index.fmf[['FineModeFraction_500nm[eta]','Total_AOD_500nm[tau_a]','Fine_Mode_AOD_500nm[tau_f]']] #to compare with 550 and 500
        self.ssa = To_D_Index.ssa[['Single_Scattering_Albedo[440nm]','Single_Scattering_Albedo[675nm]','Single_Scattering_Albedo[870nm]','Single_Scattering_Albedo[1020nm]']]
        self.aae = To_D_Index.aae[['Absorption_AOD[440nm]','Absorption_AOD[870nm]','Absorption_Angstrom_Exponent_440-870nm']]
        self.eae = To_D_Index.eae[['AOD_Extinction-Total[440nm]','AOD_Extinction-Total[870nm]','Extinction_Angstrom_Exponent_440-870nm-Total']]
        self.dep = To_D_Index.dep[['Lidar_Ratio[440nm]','Depolarization_Ratio[1020nm]']]
        self.siz = To_D_Index.siz[To_D_Index.siz.columns[5:27]]
Extract = Extract()
        
#%% AERONET : 인덱스 리셋하기 (합쳐야 해서)
class Reset_Index:
    def __init__(self):
        self.aod = Extract.aod.reset_index()
        self.ssa = Extract.ssa.reset_index()
        self.fmf = Extract.fmf.reset_index()
        self.aae = Extract.aae.reset_index()
        self.eae = Extract.eae.reset_index()
        self.dep = Extract.dep.reset_index()
        self.siz = Extract.siz.reset_index()
Reset_Index = Reset_Index()

#%% AERONET : 토탈 인덱스 생성해서 파라미터 모두 합치기
class Merge:
    def __init__(self):
        self.time_index = pd.date_range(start = '2019-01-01', end = '2022-12-31', freq='1d', name='times')
        self.time = pd.DataFrame(self.time_index)
        
        self.merge1 = pd.merge(self.time, Reset_Index.aod, how='outer')
        self.merge2 = pd.merge(self.merge1, Reset_Index.fmf, how='outer')
        self.merge3 = pd.merge(self.merge2, Reset_Index.ssa, how='outer')
        self.merge4 = pd.merge(self.merge3, Reset_Index.aae, how='outer')
        self.merge5 = pd.merge(self.merge4, Reset_Index.eae, how='outer')
        self.merge6 = pd.merge(self.merge5, Reset_Index.dep, how='outer')
        self.data = pd.merge(self.merge6, Reset_Index.siz, how='outer')

        self.data = self.data.set_index('times')
Merge = Merge()
#%% AERONET : 합쳐진 데이터로 계산해서 마무리하기
def calculation (data):
    data['angstrom_exponent'] = -np.log(data['AOD_500nm']/data['AOD_675nm'])/np.log(500/675)
    data['total_550'] = data['Total_AOD_500nm[tau_a]']*(1.1**(-1*data['angstrom_exponent']))
    data['fine_550'] = data['Fine_Mode_AOD_500nm[tau_f]']*(1.1**(-1*data['angstrom_exponent']))
    data['FMF_550'] = data['fine_550']/data['total_550']
    data['AOD_550'] = data['AOD_500nm']*(1.1**(-1*data['angstrom_exponent']))
    
    data = data.rename(columns={'Single_Scattering_Albedo[440nm]':'SSA_440'})
    data = data.rename(columns={'Absorption_Angstrom_Exponent_440-870nm':'AAE'})
    data = data.rename(columns={'Extinction_Angstrom_Exponent_440-870nm-Total':'EAE'})
    data = data.rename(columns={'Single_Scattering_Albedo[675nm]':'SSA_675'})
    data = data.rename(columns={'Single_Scattering_Albedo[870nm]':'SSA_870'})
    data = data.rename(columns={'Single_Scattering_Albedo[1020nm]':'SSA_1020'})
    
    data['scattering440'] = data['AOD_Extinction-Total[440nm]']-data['Absorption_AOD[440nm]']
    data['scattering870'] = data['AOD_Extinction-Total[870nm]']-data['Absorption_AOD[870nm]']
    data['SAE'] = -np.log(data['scattering440']/data['scattering870'])/np.log(440/870)
    return data
df_aeronet = calculation(Merge.data)
