'''Matching AERONET and SPARTAN'''
'''Sujin Eom, UNIST'''
'''230920 ~ 230925'''

#%% Packages#######################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import glob
import seaborn as sns

# pd.set_option('mode.chained_assignment', 'raise') # SettingWithCopyError
pd.set_option('mode.chained_assignment', 'warn') # SettingWithCopyWarning

#%% File Path #######################################################################################################
path_aod = '/home/sjeom/data/AERONET/all_site/All_Sites_Times_Daily_Averages_AOD15.dat' #all aod 자료
path_fmf = '/home/sjeom/data/AERONET/all_site/All_Sites_Times_Daily_Averages_SDA15.dat'
path_ssa = '/home/sjeom/data/AERONET/all_site/except_aod/19930101_20230819_'            #사이트마다 aod제외한 모든 자료
path_spa = '/home/sjeom/data/SPARTAN/all/'    

#%% Spartan and Aeronet current list ################################################################################

list_aeronet = pd.read_table('/home/sjeom/result/site_list_aeronet.csv', delimiter=',',usecols=[1,2,3])
list_spartan = pd.read_table('/home/sjeom/result/site_list_spartan.csv', delimiter=',',usecols=[1,2,3,4,5])

#%% Matching spartan and aeronet site  ################################################################################

list_spartan['AERONET_Site'] = np.nan
list_spartan['near_site'] = np.nan
#그림 인덱스 할당하기
list_spartan['ind_row'] = np.nan
list_spartan['ind_column'] = np.nan
#그림 그릴 인덱싱 : 몫과 나머지
list_spartan.ind_row = list_spartan.index//4
list_spartan.ind_column = divmod(list_spartan.index,4)[1]


for i in range (0, np.size(list_spartan.index)):
    index_a = np.where((list_aeronet['Site_Latitude(Degrees)']<(list_spartan['Latitude'].iloc[i]+0.002)) & \
             (list_aeronet['Site_Latitude(Degrees)']>(list_spartan['Latitude'].iloc[i]-0.002)))
    
    print(index_a[0])
    if len(index_a[0])>=1:
        list_spartan['AERONET_Site'][i] = list_aeronet.iloc[index_a[0][0]][0]
    if len(index_a[0])>1:
        list_spartan['near_site'][i] = list_aeronet.iloc[index_a[0][1]][0]
    if len(index_a[0])==0:
        continue

list_spartan = list_spartan.dropna(subset='AERONET_Site').reset_index(drop=True)

#%% SPARTAN : 데이터프레임 생성하기  '각각의 스파르탄 사이트 일때,' #######################################################

fig1, ax1 = plt.subplots(figsize = (110,50))
fig2, ax2 = plt.subplots(figsize = (110,50))
fig3, ax3 = plt.subplots(figsize = (110,50))
fig4, ax4 = plt.subplots(figsize = (110,50))
fig5, ax5 = plt.subplots(figsize = (110,50))

list_pm = []
list_sul = []
list_site = []
list_ssa = []

for r in list_spartan.index:
# r = list_spartan.Site_Code[0]
# r = 'ILHA'
    def filter_station (file_name):
    # file_name = f'FilterBased_ReconstrPM25_{site.inform[0]}.csv'
    # file_name = f'FilterBased_ReconstrPM25_{list_spartan.Site_Code[r]}.csv'
        path = '/home/sjeom/data/SPARTAN/all/'
        spartan_25 = path+file_name 

        ################기초 데이터 생성-날짜인덱스####################################
        data_org = pd.read_csv(spartan_25, skiprows=1, delimiter=',')
        data = data_org.copy()                                   
        df_groupby = data.groupby('Parameter_Name')

        check = 0
        for var in list(dict.fromkeys(data['Parameter_Name'])) : #나타난 순서 기준으로 중복 제거해서 나열하기
            df_var = df_groupby.get_group(var)
            
            df_var['start_date'] = df_var.Start_Year_local.astype(str)+df_var.Start_Month_local.astype(str).str.zfill(2)+df_var.Start_Day_local.astype(str).str.zfill(2)#+df_var[' Start_hour_local'].astype(str).str.zfill(2)
            df_var['start_date'] = pd.to_datetime(df_var.start_date, format='%Y%m%d')
            df_var['end_date'] = df_var.End_Year_local.astype(str)+df_var.End_Month_local.astype(str).str.zfill(2)+df_var.End_Day_local.astype(str).str.zfill(2)#+df_var['End_hour_local'].astype(str).str.zfill(2)
            df_var['end_date'] = pd.to_datetime(df_var.end_date, format='%Y%m%d')

            df_var.rename(columns={'Value':var}, inplace=True)
            df_var = df_var[[var, 'start_date', 'end_date', 'Filter_ID']]

            if check == 0:
                merge_df = df_var
                check+=1
            else:
                merge_df = pd.merge(merge_df, df_var, how='outer', on=['start_date','end_date','Filter_ID'])
        merge_df.set_index('start_date', inplace=True)
        merge_df['start_date'] = merge_df.index
        return merge_df
    df_filter = filter_station (f'FilterBased_ReconstrPM25_{list_spartan.Site_Code[r]}.csv')  #필터자료 정렬

    index_aeronet = list_spartan.AERONET_Site[r]  #해당 스파르탄사이트 r이 가지는 에어로넷 사이트의 이름
    if pd.isna(index_aeronet) == False: #에어로넷 사이트가 스파르탄 근처에 있는 경우 (nan이 아닌경우)
        path_ssa_2 = f'{path_ssa}{index_aeronet}.all' #ssa의 경우, 각 사이트별로 가져올수있음 (자료 이름별로)
        data_org_ssa = pd.read_csv(path_ssa_2, skiprows=6, delimiter=',', encoding='utf-8') #일치하는 사이트에 대한 aod, fmf, ssa 자료 가져오기
        data_org_aod = pd.read_table(path_aod, sep=",", skiprows=6)
        data_org_fmf = pd.read_table(path_fmf, sep=",", skiprows=6)
        
        df_group_aer = data_org_aod.groupby('AERONET_Site') #해당 스파르탄&에어로넷 사이트 마다의 그룹으로 에어로넷 자료 가져오기
        df_group_fmf = data_org_fmf.groupby('AERONET_Site')
        df_aer = df_group_aer.get_group(index_aeronet)
        df_fmf = df_group_fmf.get_group(index_aeronet)
        df_ssa = data_org_ssa

        class To_D_Index:
            def __init__(self):
                self.aod = df_aer.replace(to_replace = -999, value = np.nan)
                self.aod['times'] = pd.to_datetime(self.aod['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
                self.aod = self.aod.set_index('times')
                
                self.fmf = df_fmf.replace(to_replace = -999, value = np.nan) #FMF만 Date 칼럼 이름이 다름 주의하기
                self.fmf['times'] = pd.to_datetime(self.fmf['Date_(dd:mm:yyyy)'], format = "%d:%m:%Y")
                self.fmf = self.fmf.set_index('times')        

                self.ssa = df_ssa.replace(to_replace = -999, value = np.nan)
                self.ssa['times'] = pd.to_datetime(self.ssa['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
                self.ssa = self.ssa.set_index('times')
        To_D_Index = To_D_Index()
        
        class Extract:
            def __init__(self):
                self.aod = To_D_Index.aod[['AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm','AOD_1020nm','Precipitable_Water(cm)','440-870_Angstrom_Exponent']]
                self.fmf = To_D_Index.fmf[['FineModeFraction_500nm[eta]','Total_AOD_500nm[tau_a]','Fine_Mode_AOD_500nm[tau_f]']] #to compare with 550 and 500
                self.ssa = To_D_Index.ssa[['Single_Scattering_Albedo[440nm]','Single_Scattering_Albedo[675nm]','Single_Scattering_Albedo[870nm]','Single_Scattering_Albedo[1020nm]',\
                                    'Absorption_AOD[440nm]','Absorption_AOD[870nm]','Absorption_AOD[1020nm]','Absorption_Angstrom_Exponent_440-870nm',\
                                    'AOD_Extinction-Total[440nm]','AOD_Extinction-Total[870nm]','AOD_Extinction-Total[1020nm]','Extinction_Angstrom_Exponent_440-870nm-Total',\
                                        'Lidar_Ratio[440nm]','Depolarization_Ratio[1020nm]','0.050000', '0.065604', '0.086077', '0.112939', '0.148184', \
                                            '0.194429', '0.255105', '0.334716', '0.439173', '0.576227','0.756052', '0.991996', '1.301571', '1.707757', \
                                                '2.240702', '2.939966', '3.857452', '5.061260', '6.640745', '8.713145', '11.432287', '15.000000']]
        Extract = Extract()

        class Merge: #에어로넷자료만 모으기
            def __init__(self):
                self.time_index = pd.date_range(start = '2013-01-01', end = '2023-12-31', freq='1d', name='times')
                self.time = pd.DataFrame(self.time_index)
                self.time = self.time.set_index('times',drop=True)
                self.join_aod = self.time.join(Extract.aod, how='left') #join으로 인덱스 기준으로 합침
                self.join_aod_fmf = self.join_aod.join(Extract.fmf, how='left')
                self.data = self.join_aod_fmf.join(Extract.ssa, how='left')
        Merge = Merge()

        def calculation (data): #SAE등등 계산하기
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
            data['scattering1020'] = data['AOD_Extinction-Total[1020nm]']-data['Absorption_AOD[1020nm]']
            
            data['SAE'] = -np.log(data['scattering440']/data['scattering870'])/np.log(440/870)
            return data
        df_aeronet = calculation(Merge.data)

        def Make_full_df (df_filter, df_aeronet, list_spartan): #유효한 데이터 모아서 9일자료들 완전히 합치기
            
            for i in range (0, np.size(df_filter.index)):
                if df_filter['start_date'][i]+timedelta(days = 8) != df_filter['end_date'][i]:
                    print(df_filter['start_date'][i], df_filter['end_date'][i])
                    df_filter[df_filter.columns[0]].iloc[i] = np.nan                       #만약 9일데이터가 아니라면 PM부분 nan값으로 바꾸기
                else:
                    continue                    



                #####그 외의 invalid 기간 - 정전 등 '유니스트'
                # 2023년 1월 12일 정전 - 삭제필요
                # 2023년 4월 25일 관측 시작한 필터 012의 1번째 period 삭제필요
            print(r)
            if list_spartan.Site_Code[r] == 'KRUL':
                day_invalid_org = ['2023-01-07']#,'2023-04-25']                         다음 데이터 추가되면 열기
                day_invalid = pd.to_datetime(day_invalid_org, format = "%Y-%m-%d")
                for d in range (0, np.size(day_invalid)):
                    d_index = np.where(df_filter.index == f'{day_invalid[d]}')[0][0]  
                    df_filter[df_filter.columns[0]].iloc[d_index] = np.nan                     #만약 인덱스가 invalid 리스트에 있다면

            #PM없는 행은 삭제
            df_filter_pm_x = df_filter.dropna(subset = ['Filter PM2.5 mass'], axis=0)
                
            #valid 기간만 추출하기
            day_list = df_filter_pm_x.index
            day_list_e = df_filter_pm_x.end_date
            
            a_list = [] #9일 기준으로 두지 않고 자료 최대한 살려서 평균하기
            df_aeronet['color'] = np.nan #스파르탄 기간 안에 있는 데이터들은 색깔 칼럼에 표시
            for a in range (len(day_list)):
                #만약 9일 데이터라면 파란색, 아니라면 빨간색으로 두기
                if day_list[a]+timedelta(days = 8) == day_list_e[a]:
                    df_aeronet['color'].loc[day_list[a]:day_list_e[a]] = 'blue' 
                else:
                    df_aeronet['color'].loc[day_list[a]:day_list_e[a]] = 'red'
                globals()['period_'+str(a)] = df_aeronet.loc[day_list[a]:day_list_e[a]]
                a_list.append(globals()['period_'+str(a)][globals()['period_'+str(a)].columns[:-1]].mean()) #color 칼럼만 빼고(-1) 각 기간별로 평균함
                       
            df_aeronet['color'] = df_aeronet['color'].fillna('lightgrey') #스파르탄 기간에 해당 안되는 것들은 회색으로 두기
            try:
                df_aeronet_nine = np.vstack(a_list)
                df_aeronet_nine = pd.DataFrame(df_aeronet_nine)  
                df_aeronet_nine.columns = df_aeronet.columns[:-1]
                df_aeronet_nine.index = pd.DatetimeIndex(day_list)
                df_database_total = pd.concat([df_filter_pm_x[df_filter_pm_x.columns[0:9]], df_aeronet_nine], axis=1)
            except:
                df_database_total = df_filter_pm_x[df_filter_pm_x.columns[0:9]]
                # df_aeronet_nine = pd.DataFrame()
                # df_aeronet_nine.columns = df_aeronet.columns[:-1]
                # df_aeronet_nine.index = pd.DatetimeIndex(day_list)
            #필터, 에어로넷 모두 합치기
            # df_database_total = pd.concat([df_filter_pm_x[df_filter_pm_x.columns[0:9]], df_aeronet_nine], axis=1)

            return df_database_total, day_list, df_aeronet, list_spartan
        f, day_list, f_aeronet, list_s = Make_full_df(df_filter, df_aeronet, list_spartan)
