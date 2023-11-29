'''Matching AERONET and SPARTAN chem'''
'''Sujin Eom, UNIST'''
'''231124 ~ '''

#%% Packages################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import glob
import seaborn as sns
# pd.set_option('mode.chained_assignment', 'raise') # SettingWithCopyError
pd.set_option('mode.chained_assignment', 'warn') # SettingWithCopyWarning

#%% File Path ##############################################################################################
path_aod = '/home/sjeom/data/AERONET/AOD/AOD15/DAILY/19930101_20231028_' # .lev15
path_fmf = '/home/sjeom/data/AERONET/SDA/SDA15/DAILY/19930101_20231028_' # .ONEILL_lev15
path_ssa = '/home/sjeom/data/AERONET/INV/LEV15/ALL/DAILY/19930101_20231028_'  # .all   
path_spa = '/home/sjeom/data/SPARTAN/all/'
path_che = '/home/sjeom/data/SPARTAN/all_chem/'    

#%% Spartan and Aeronet current list #######################################################################
#에어로넷과 스파르탄의 위경도 정보 가져와서 가장 가까운 사이트로 매칭하기
list_aeronet = pd.read_table('/home/sjeom/result/site_list_aeronet.csv', delimiter=',',usecols=[1,2,3]) #에어로넷 사이트 목록 및 위경도
list_spartan = pd.read_table('/home/sjeom/result/site_list_spartan.csv', delimiter=',',usecols=[1,2,3,4,5])
list_spartan['AERONET_Site'] = np.nan
list_spartan['near_site'] = np.nan

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
list_spartan = list_spartan.dropna(subset='AERONET_Site').reset_index(drop=True)                        #스파르탄 사이트 근처에 해당하는 에어로넷 리스트 만들기 

#%% DEFINITION ##############################################################################################

#### spartan processing #####
def Filter_starion (file_name):
    if file_name.find('Reconstr')!= -1:
        path = '/home/sjeom/data/SPARTAN/all/'
    else:
        path = '/home/sjeom/data/SPARTAN/all_chem/'
    spartan_25 = path+file_name 

    ################기초 데이터 생성-날짜인덱스####################################
    data_org = pd.read_csv(spartan_25, skiprows=3, delimiter=',',encoding='utf8')
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
    del_duplicate = merge_df.drop_duplicates(['start_date'])
    del_duplicate.set_index('start_date', inplace=True)
    del_duplicate['start_date'] = del_duplicate.index       #중복된 열이 왜 생기는지를 모르겠지만 일단 제거함
    f = del_duplicate.fillna(0)
    return f
#### aeronet calculating ####
def Calculation (data): 
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
#### spartan + aeronet ######
def Make_full_df (df_filter, df_aeronet, list_spartan): 
    print(site_code)
    for i in range (0, np.size(df_filter.index)):
        if df_filter.index[i]+timedelta(days = 8) != df_filter['end_date'][i]:                      #유효한 데이터 모아서 9일자료들 완전히 합쳐야함
            df_filter[df_filter.columns[0]].iloc[i] = np.nan                                        #만약 9일데이터가 아니라면 PM부분 nan값으로 바꾸기
        else:
            continue                    
    ###################### invalid 기간 삭제하기 ############################
                #########'유니스트'지점 정전 ################
                # 2023년 1월 12일 정전 - 삭제필요
                # 2023년 4월 25일 관측 시작한 필터 012의 1번째 period 삭제필요
    if site_code == 'KRUL':
        day_invalid_org = ['2023-01-07']#,'2023-04-25']  다음 데이터 추가되면 열기
        day_invalid = pd.to_datetime(day_invalid_org, format = "%Y-%m-%d")
        for d in range (0, np.size(day_invalid)):
            d_index = np.where(df_filter.index == f'{day_invalid[d]}')[0][0]  
            df_filter[df_filter.columns[0]].iloc[d_index] = np.nan                                  #만약 인덱스가 invalid 리스트에 있다면 nan으로

    ########################### PM없는 행은 삭제 #############################
    df_filter_pm_x = df_filter.dropna(subset = ['Filter PM2.5 mass'], axis=0)                       
        
    day_list = df_filter_pm_x.index                                                                 #valid 기간만 추출한 daylist
    day_list_e = df_filter_pm_x.end_date
    a_list = []                                                                                     #평균할 자료 모으기
    a_base = df_aeronet.mean()
    a_base.loc[:] = np.nan

    for a in range (len(day_list)):
        globals()['period_'+str(a)] = df_aeronet.loc[day_list[a]:day_list_e[a]]
        ########## 해당 기간에 자료가 2개부터여야 평균하기 ###################
        if globals()['period_'+str(a)].SSA_440.count() > 1:
            a_list.append(globals()['period_'+str(a)].mean())                                       #각 기간별로 평균함 
        ########## 자료가 충분하지 않은 경우에 칼럼만 남겨서 추가하기 ########
        else:
            a_list.append(a_base) 

    ################### 스파르탄 기간에 대해서 평균된 AERONET 자료 합치기 ####
    try:
        df_aeronet_nine = np.vstack(a_list)
        df_aeronet_nine = pd.DataFrame(df_aeronet_nine)  
        df_aeronet_nine.columns = df_aeronet.columns
        df_aeronet_nine.index = pd.DatetimeIndex(day_list)
    except:
        df_aeronet_nine = pd.DataFrame()
        df_aeronet_nine.index = pd.DatetimeIndex(day_list)

    ################## 스파르탄과 에어로넷 합치기 #############################
    df_database_total = pd.concat([df_filter_pm_x, df_aeronet_nine], axis=1)
    return df_database_total, day_list, df_aeronet, list_spartan, df_aeronet_nine, a_list

#%% PROCESSING ##############################################################################################
valid_list = ['AEAZ', 'BDDU', 'CHTS', 'IDBD', 'ILNZ', 'INKA', 'KRSE', 'KRUL', 'MXMC', 'NGIL', 'SGSU']   #자료 수가 10 이상인 스파르탄 사이트 리스트
ind = 0
for site_code in valid_list:

    df_reconst = Filter_starion (f'FilterBased_ReconstrPM25_{site_code}.csv')  #필터자료 정렬
    df_chemical = Filter_starion (f'FilterBased_ChemSpecPM25_{site_code}.csv')  #이온자료 정렬
    ########################### 스파르탄 reconst자료와 chemical 자료 합치기 #################################
    df_filter = df_reconst[df_reconst.columns[0:]].join(df_chemical[df_chemical.columns[3:-1]],how='outer')


    ########################### 에어로넷 자료 얻기 ##########################################################
    index_aeronet = list_spartan['AERONET_Site'][np.where(list_spartan.Site_Code == site_code)[0][0]]   #해당 스파르탄사이트 각각이 가지는 에어로넷 사이트의 이름
    path_ssa_org = f'{path_ssa}{index_aeronet}.all'                                                     #ssa의 경우, 각 사이트별로 가져올수있음 (자료 이름별로)
    data_org_ssa = pd.read_csv(path_ssa_org, skiprows=6, delimiter=',', encoding='utf-8')               #일치하는 사이트에 대한 aod, fmf, ssa 자료 가져오기
    data_org_aod = pd.read_table(f'{path_aod}{index_aeronet}.lev15', sep=",", skiprows=6, encoding='utf-8')
    data_org_fmf = pd.read_table(f'{path_fmf}{index_aeronet}.ONEILL_lev15', sep=",", skiprows=6, encoding='utf-8')
    ########################### 에어로넷 자료 인덱스 지정 및 필요한 칼럼 불러오기 ###########################
    class To_D_Index:
        def __init__(self):
            self.aod = data_org_aod.replace(to_replace = -999, value = np.nan)
            self.aod['times'] = pd.to_datetime(self.aod['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
            self.aod = self.aod.set_index('times')
            
            self.fmf = data_org_fmf.replace(to_replace = -999, value = np.nan) #FMF만 Date 칼럼 이름이 다름 주의하기
            self.fmf['times'] = pd.to_datetime(self.fmf['Date_(dd:mm:yyyy)'], format = "%d:%m:%Y")
            self.fmf = self.fmf.set_index('times')        

            self.ssa = data_org_ssa.replace(to_replace = -999, value = np.nan)
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
    ########################### 에어로넷 자료 합치기 ########################################################
    class Merge: 
        def __init__(self):
            self.time_index = pd.date_range(start = '2013-01-01', end = '2023-12-31', freq='1d', name='times')
            self.time = pd.DataFrame(self.time_index)
            self.time = self.time.set_index('times',drop=True)
            self.join_aod = self.time.join(Extract.aod, how='left')                                     #join으로 인덱스 기준으로 합침
            self.join_aod_fmf = self.join_aod.join(Extract.fmf, how='left')
            self.data = self.join_aod_fmf.join(Extract.ssa, how='left')
    Merge = Merge()
    ########################### 에어로넷 계산 데이터 생성하기 (SAE등) #######################################
    df_aeronet = Calculation(Merge.data)

    ########################### 스파르탄 기간에 맞추어 9일 평균자료 만들기 ##################################
    f, day_list, f_aeronet, list_s, df_aeronet_nine, a_list = Make_full_df(df_filter, df_aeronet, list_spartan)

    
    ############################ 사이트별로 자료 필터링 및 성분별 delta 계산하기 ############################
    try:
        f['ratio'] = f[' BC PM2.5']/(f[' Sulfate PM2.5']+f[' BC PM2.5'])
        f['type_ratio'] = f['BC PM2.5']/(f['Ammoniated Sulfate']+f['BC PM2.5'])
        f['bc/sul'] = f[' BC PM2.5']/f[' Sulfate PM2.5']
    except:
        continue
    
    !!!!!!!!!!!!!!!!!######### BC또는 Am Sulfate 둘중 하나가 존재하지 않는다면 자료 없애기 ########
    f['Filter PM2.5 mass'][(f['type_ratio']==1) | (f['type_ratio']==0)] = np.nan
    
    ################### 낮은 오염인 경우 삭제하기 ################################
    f['Filter PM2.5 mass'][f['Filter PM2.5 mass']<10] = np.nan
    f['Filter PM2.5 mass'][f['AOD_440nm']<0.4] = np.nan

    ################### 사이트별로 delta 구하기 ##################################
    f['type_ratio_del'] = f['type_ratio']-f['type_ratio'].mean()
    f['ratio_del'] = f['ratio']-f['ratio'].mean()
    f['bc/sul_del'] = f['bc/sul']-f['bc/sul'].mean()
    f['ssa440_del'] = f['SSA_440']-f['SSA_440'].mean()
    f['ssa1020_del'] = f['SSA_1020']-f['SSA_1020'].mean()
    f['bc_del'] = f['BC PM2.5']-f['BC PM2.5'].mean()
    f['sul_del'] = f[' Sulfate PM2.5']-f[' Sulfate PM2.5'].mean()
    f['amsul_del'] = f['Ammoniated Sulfate']-f['Ammoniated Sulfate'].mean()

    f = f.dropna(subset = ['Filter PM2.5 mass'], axis=0)                                                #쓸만한 자료만 남기기
    f_tot = f.reset_index(drop=True)

    #################################### 차례로 모든 사이트 자료 합치기 ######################################
    if ind == 0:
        merge_f = f_tot
        ind+=1
    else:
        merge_f = pd.merge(merge_f, f_tot, how='outer')
        ind+=1
    
    ################################# 각 사이트마다 그림그리기 아래에 나타냄 ##################################
    ###########################################################################################################
    #######################                     Figure 1                          #############################
    ###########################################################################################################
    ################# x축 : BC/(BC+AmSulf)
    ################# y축 : SSA 440 delta
    ################# 컬러: FMF 500, cmap : Greens

    fig1, ax1 = plt.subplots(figsize = (10,8))
    try:
        ssa_list = f['ssa440_del']
        ratio_list = f['type_ratio_del']
        color_list = f['Fine Soil']/(f['Fine Soil']+f['Ammoniated Sulfate'])
        circle_size = f['Filter PM2.5 mass']
        df_correlation = pd.DataFrame([ssa_list.reset_index(drop=True), ratio_list.reset_index(drop=True)]).T
        df_correlation = df_correlation[np.isfinite(df_correlation).all(1)]
        
        image1 = ax1.scatter(ratio_list,ssa_list,\
                        c=color_list,vmin=0,vmax=1, cmap='jet', marker='o', edgecolor='grey', s=circle_size*10, zorder=2) #"$\u25EF$"  cmap='Greens',vmin=0,vmax=1, 
        image1.figure.axes[0].tick_params(axis="both", labelsize=18)
        plt.text(0.05,0.08,'R='+str(round(np.ma.corrcoef(df_correlation[ssa_list.name], df_correlation[df_correlation.columns[1]])[0,1],3)), fontsize=30)
        plt.text(0.05,0.06,'N='+str(df_correlation.count()[0]), fontsize=30)
        plt.text(0.05, 0.04, 'SSA='+str(round(f['SSA_440'].mean(),3)), fontsize=30)
        plt.text(0.05, 0.02, 'ratio='+str(round(f['type_ratio'].mean(),3)), fontsize=30)

        ax1.set_title(site_code+'-'+index_aeronet, fontsize=25, fontweight='bold')
        ax1.set_ylim(-0.1,0.1)
        ax1.set_ylabel('AERONET SSA 440 del', fontsize=22)
        plt.yticks(np.arange(-0.1,0.11,0.02),fontsize=17)
        ax1.set_xlim(-0.5,0.5)
        plt.xticks(np.arange(-0.5,0.501,0.1),fontsize=17)
        plt.grid(True, color='black', alpha=0.2, linestyle='--')
        ax1.set_xlabel('BC / {BC+AmSulf} del', fontsize=22)
        c1 = fig1.colorbar(image1, shrink=1, aspect=10,ticks=[0,0.2,0.4,0.6,0.8,1.0,1.2])
        c1.ax.tick_params(labelsize=15)
        c1.set_label('Soil/Soil+Amsulf', fontsize=22)
        c1.set_ticklabels(['0','0.2','0.4','0.6','0.8','1.0','1.2'])
        plt.plot([0,0],[-0.1,0.1],'-',color='blue',linewidth=1,alpha = 0.8)
        plt.plot([-3,7],[0,0],'-',color='blue',linewidth=1,alpha = 0.8)
        # plt.savefig(f'/home/sjeom/result/spartan/bc_bc+amsulf_del_aeronet_{site_code}.png', dpi=300, bbox_inches='tight')
    except:
        print(f'{site_code} crashed')
    
    plt.show()      

    ###########################################################################################################
    #######################                     Figure 2                          #############################
    ###########################################################################################################
    ################# x축 : amsulf del
    ################# y축 : bc del
    ################# 컬러: ssa 440 del, cmap : coolwarm

    fig2, ax2 = plt.subplots(figsize = (10,8))
    try:
        x_list = f['amsul_del']
        y_list = f['bc_del']
        color_list = f['ssa440_del']
        circle_size = f['Filter PM2.5 mass']
        df_correlation = pd.DataFrame([ssa_list.reset_index(drop=True), ratio_list.reset_index(drop=True)]).T
        df_correlation = df_correlation[np.isfinite(df_correlation).all(1)]
        
        image2 = ax2.scatter(x_list,y_list,\
                        c=color_list,vmin=-0.1,vmax=0.1, cmap='coolwarm', marker='o', edgecolor='grey', s=circle_size*10, zorder=2) #"$\u25EF$"  cmap='Greens',vmin=0,vmax=1, 
        image2.figure.axes[0].tick_params(axis="both", labelsize=18)
        plt.text(-9,13,'R='+str(round(np.ma.corrcoef(df_correlation[ssa_list.name], df_correlation[df_correlation.columns[1]])[0,1],3)), fontsize=30)
        plt.text(-9,11,'N='+str(df_correlation.count()[0]), fontsize=30)
        plt.text(-9, 9, 'SSA='+str(round(f['SSA_440'].mean(),3)), fontsize=30)
        plt.text(-9, 7, 'BC='+str(round(f['BC PM2.5'].mean(),1)), fontsize=30)
        plt.text(-9, 5, 'AmS-='+str(round(f['Ammoniated Sulfate'].mean(),1)), fontsize=30)

        ax2.set_title(site_code+'-'+index_aeronet, fontsize=25, fontweight='bold')
        ax2.set_ylim(-15,15)
        ax2.set_ylabel('BC del', fontsize=22)
        plt.yticks(np.arange(-15,15.1,3),fontsize=17)
        ax2.set_xlim(-10,10)
        plt.xticks(np.arange(-10,10.1,1),fontsize=17)
        plt.grid(True, color='black', alpha=0.2, linestyle='--')
        ax2.set_xlabel('AmSulf del', fontsize=22)
        c2 = fig2.colorbar(image2, shrink=1, aspect=10,ticks=[-0.1,-0.08,-0.06,-0.04,-0.02,0,0.02,0.04,0.06,0.08,0.1])
        c2.ax.tick_params(labelsize=15)
        c2.set_label('SSA 440 delta', fontsize=22)
        c2.set_ticklabels(['-0.1','-0.08','-0.06','-0.04','-0.02','0','0.02','0.04','0.06','0.08','0.1'])
        plt.plot([0,0],[-15,15],'-',color='blue',linewidth=1,alpha = 0.8)
        plt.plot([-10,10],[0,0],'-',color='blue',linewidth=1,alpha = 0.8)
        # plt.savefig(f'/home/sjeom/result/spartan/bc_sul_mass_del_aeronet_{site_code}.png', dpi=300, bbox_inches='tight')
    except:
        print(f'{site_code} crashed')
    
    plt.show()



####################### 모든 사이트의 자료 합침 ##############################################################
f_all = merge_f.set_index('start_date')

#%%#################### 합쳐진 데이터로 그림 1개 그리기 ######################################################

########## SSA-FMF 임의 그룹에 대해서 색깔 지정 후 그룹 평균 #################################################
f_all['group'] = None
f_all['group'][(f_all['FineModeFraction_500nm[eta]']>0.7) & (f_all['SSA_440']>0.94)] = 'black'
f_all['group'][(f_all['FineModeFraction_500nm[eta]']>0.7) & (f_all['SSA_440']<0.94)] = 'red'
f_all['group'][(f_all['FineModeFraction_500nm[eta]']<0.7) & (f_all['SSA_440']>0.94)] = 'orange'
f_all['group'][(f_all['FineModeFraction_500nm[eta]']<0.7) & (f_all['SSA_440']<0.94)] = 'green'
f_all = f_all.dropna(subset = ['group'], axis=0)
f_group = f_all.groupby('group').mean()

################### 합쳐진 데이터로 ratio와 delta 계산하기 ###################################################
f_all['all_type_ratio_del'] = f_all['type_ratio']-f_all['type_ratio'].mean()
f_all['all_ratio_del'] = f_all['ratio']-f_all['ratio'].mean()
f_all['all_bc/sul_del'] = f_all['bc/sul']-f_all['bc/sul'].mean()
f_all['all_ssa440_del'] = f_all['SSA_440']-f_all['SSA_440'].mean()
f_all['all_bc_del'] = f_all['BC PM2.5']-f_all['BC PM2.5'].mean()
f_all['all_sul_del'] = f_all[' Sulfate PM2.5']-f_all[' Sulfate PM2.5'].mean()



##############################################################################################################
############################ AAE SAE에 맞추어 광학유형 분류하기 ##############################################
##############################################################################################################

######### 칼럼 만들기 ###########
f_all['type'] = None
f_all['bc'] = np.nan
f_all.astype({'type':'object'})
######## AAE-SAE criteria #######
for index, row in f_all.iterrows():
    bc = np.nan # <-- bc 임시 변수
    if row['AOD_440nm'] <= 0.4:                                                                         ##classification AOD minimum criteria
         f_all.at[index, 'type'] = 'Low'

    if row['AOD_440nm'] > 0.4:
        if row['SAE'] <= 0 and row['AAE'] >= 2:
            f_all.at[index, 'type'] = 'Dust'

        if row['SAE'] <= 1.5 and row['AAE'] >= 1.5 \
            and row['FineModeFraction_500nm[eta]'] < 0.4:
            f_all.at[index, 'type'] = 'Dust'

        if row['SAE']<=1.5 and row['AAE']>=1.5 \
            and row['FineModeFraction_500nm[eta]']>=0.4 :
            f_all.at[index, 'type'] = 'BC+BrC'

        if row['SAE']<1 and row['AAE']<1:
            f_all.at[index, 'type'] = 'Uncertain'       

        if row['SAE']>=1 and row['AAE']<1:
            f_all.at[index, 'type'] = 'NA'

        if row['SAE']<1.5 and row['AAE']>=1.0 \
            and row['AAE']<1.5 and \
                row['AAE']>row['SAE'] \
                    and row['FineModeFraction_500nm[eta]']>0.6:     
            bc = 1  # <-- 임시 변수에 저장

        if row['SAE']<1.5 and row['AAE']>=1.0 \
            and row['AAE']<1.5 and \
            row['AAE'] > row['SAE'] \
                and row['FineModeFraction_500nm[eta]']<=0.6:        
            f_all.at[index, 'type'] = 'Uncertain'

        if row['SAE']>=1 and row['AAE']>=1.0 \
            and row['AAE']<1.5 and \
            row['AAE']<=row['SAE']:        
            bc = 1

        if row['SAE']>=1.5 and row['AAE']>1.5:
            bc = 1
            
        if bc == 1:
            f_all.at[index, 'bc'] = 1    # 임시 변수 값에 따라 df에 값 지정

        if bc == 1 and row['AAE']>=2:   # 임시 변수로 비교
            f_all.at[index, 'type'] = 'BrC'

        if bc == 1 and 1.5<=row['AAE']<2:
            f_all.at[index, 'type'] = 'BC+BrC'

        if bc == 1 and row['AAE']<1.5:
            f_all.at[index, 'type'] = 'BC'

###############################################################################################################
###############################################################################################################



############################ 그룹바이 된 그룹들 가져오기 #####################################################
f_black = f_all.groupby('group').get_group('black')
f_red = f_all.groupby('group').get_group('red')
f_orange = f_all.groupby('group').get_group('orange')
f_green = f_all.groupby('group').get_group('green')





#%%############################################################################################################
#######################                     Figure 17                          ################################
###############################################################################################################
################# x축 : BC/(BC+AmSulf)
################# y축 : SSA 440 delta
################# 컬러: SSA-FMF 로 나눠진 그룹 (빨,노,초,검) 

fig17, ax17 = plt.subplots(figsize = (10,10))
try:
    ssa_list = f_all['all_ssa440_del']
    ratio_list = f_all['all_type_ratio_del']
    color_list = f_all['group']
    circle_size = f_all['Filter PM2.5 mass']
    df_correlation = pd.DataFrame([ssa_list.reset_index(drop=True), ratio_list.reset_index(drop=True)]).T
    df_correlation = df_correlation[np.isfinite(df_correlation).all(1)]
    
    image17 = ax17.scatter(ratio_list,ssa_list,\
                    c=color_list, marker='o', edgecolor='grey', s=circle_size*10, zorder=2) #"$\u25EF$"  cmap='Greens',vmin=0,vmax=1, 
    image17.figure.axes[0].tick_params(axis="both", labelsize=18)
    plt.text(0.05,0.08,'R='+str(round(np.ma.corrcoef(df_correlation[ssa_list.name], df_correlation[df_correlation.columns[1]])[0,1],3)), fontsize=30)
    plt.text(0.05,0.07,'N='+str(df_correlation.count()[0]), fontsize=30)
    plt.text(0.05, 0.06, 'SSA='+str(round(f_all['SSA_440'].mean(),3)), fontsize=30)
    plt.text(0.05,0.05, 'Ratio='+str(round(f_all['type_ratio'].mean(),2)), fontsize=30)

    ax17.set_title('All Site Group', fontsize=25, fontweight='bold')
    ax17.set_ylim(-0.1,0.1)
    ax17.set_ylabel('AERONET SSA 440 del', fontsize=22)
    plt.yticks(np.arange(-0.1,0.11,0.02),fontsize=17)
    ax17.set_xlim(-0.5,0.5)
    plt.xticks(np.arange(-0.5,0.501,0.1),fontsize=17)
    plt.grid(True, color='black', alpha=0.2, linestyle='--')
    ax17.set_xlabel('BC / {BC+AmSulf} del', fontsize=22)
    
    plt.plot([0,0],[-0.1,0.1],'-',color='blue',linewidth=1,alpha = 0.8)
    plt.plot([-3,7],[0,0],'-',color='blue',linewidth=1,alpha = 0.8)
    # plt.savefig(f'/home/sjeom/result/spartan/bc_bc+amsulf_del_fmfssa_group_{site_code}.png', dpi=300, bbox_inches='tight')
except:
    print(f'{site_code} crashed')

plt.show()

#%%############################################################################################################
#######################                     Figure 18                          ################################
###############################################################################################################
################# x축 : SSA 파장 440,675,870,1020 
################# y축 : SSA 값
################# 컬러: SSA-FMF 로 나눠진 그룹 (빨,노,초,검) 
################# 그룹별로 그림 따로 나옴 (4 in 1)
################# 각 그림마다의 SSA 파장별 평균값을 색깔로 표시, 나머지는 회색

fig18, ax18 = plt.subplots(2,2, figsize = (20,20))
group = ['black','red','green','orange']

########## 컬러와 그룹에 따른 그림 위치 정해주기 ########
for g in group:   
    if g == 'orange':
        a, b, c = 0, 0, 0
    if g == 'black':
        a, b, c = 0, 1, 1  
    if g == 'green':
        a, b, c = 1, 0, 2
    if g == 'red':
        a, b, c = 1, 1, 3

    f_g = globals()['f_'+g]
    for e in range (0, np.size(f_g.index)):
        if f_g['SSA_440'][e] > 0:
            image18 = ax18[a,b].scatter([440,675,870,1020],f_g[['SSA_440','SSA_675','SSA_870','SSA_1020']].iloc[e]\
                    ,c='grey', marker='o', s=50, zorder=2, alpha=0.1)
            ax18[a,b].plot([440,675,870,1020],f_g[['SSA_440','SSA_675','SSA_870','SSA_1020']].iloc[e], linewidth=0.8, \
                    linestyle='--', color='grey', zorder=1)
            #평균값
            ax18[a,b].scatter([440,675,870,1020], [f_g['SSA_440'].mean(),f_g['SSA_675'].mean(),f_g['SSA_870'].mean(),f_g['SSA_1020'].mean()],\
                              c=g,s=200,marker='o')
            ax18[a,b].plot([440,675,870,1020], [f_g['SSA_440'].mean(),f_g['SSA_675'].mean(),f_g['SSA_870'].mean(),f_g['SSA_1020'].mean()],\
                              linewidth=1.5, linestyle='-', color=g, zorder=1)
            
            ax18[a,b].text(440,f_g['SSA_440'].mean()+0.01,str(round(f_g['SSA_440'].mean(),2)), fontsize=20)
            ax18[a,b].text(675,f_g['SSA_675'].mean()+0.01,str(round(f_g['SSA_675'].mean(),2)), fontsize=20)
            ax18[a,b].text(870,f_g['SSA_870'].mean()+0.01,str(round(f_g['SSA_870'].mean(),2)), fontsize=20)
            ax18[a,b].text(1020,f_g['SSA_1020'].mean()+0.01,str(round(f_g['SSA_1020'].mean(),2)), fontsize=20)

            ax18[a,b].set_ylim(0.7,1)
            ax18[a,b].set_xticks([440,675,870,1020])
            ax18[a,b].set_xlabel('wavelength [nm]', fontsize=20) 
            ax18[a,b].set_ylabel('SSA', fontsize=20)     
            image18.figure.axes[c].tick_params(axis="both", labelsize=20)      

#%%############################################################################################################
#######################                     Figure 19                          ################################
###############################################################################################################
################# x축 : BC/(Bc+AmSulf)
################# y축 : SSA 440 delta
################# 컬러: Fine Soil / (AmSulf+FineSoil), cmap=jet
################# soil 비중 제한으로 (0.2) 그림 다르게 뽑을수있음

fig19, ax19 = plt.subplots(figsize = (12,10))
f_all['soil_sul'] = f_all['Fine Soil']/(f_all['Fine Soil']+f_all['Ammoniated Sulfate'])
s_list = []
soil_list = []

for v in range (0, np.size(f_all.index)):
    if f_all['soil_sul'][v] < 0.2:                                                                      # soil 비중 제한하기
        image19 = ax19.scatter(f_all['all_type_ratio_del'][v],f_all['all_ssa440_del'][v],\
                        c=f_all['soil_sul'][v], marker='o', edgecolor='grey',vmin=0,vmax=1, cmap='jet',s=f_all['Filter PM2.5 mass'][v]*10, zorder=2) #"$\u25EF$"  cmap='Greens',vmin=0,vmax=1, 
        image19.figure.axes[0].tick_params(axis="both", labelsize=18)
        s_list.append(f_all['all_ssa440_del'][v])
        soil_list.append(f_all['all_type_ratio_del'][v])

    ax19.set_title('All Site Group', fontsize=25, fontweight='bold')
    ax19.set_ylim(-0.1,0.1)
    ax19.set_ylabel('AERONET SSA 440 del', fontsize=22)
    plt.yticks(np.arange(-0.1,0.11,0.02),fontsize=17)
    ax19.set_xlim(-0.5,0.5)
    plt.xticks(np.arange(-0.5,0.501,0.1),fontsize=17)
    plt.grid(True, color='black', alpha=0.2, linestyle='--')
    ax19.set_xlabel('BC / {BC+AmSulf} del', fontsize=22)
    
    plt.plot([0,0],[-0.1,0.1],'-',color='blue',linewidth=1,alpha = 0.8)                                 # delta의 중앙선 표시하기
    plt.plot([-3,7],[0,0],'-',color='blue',linewidth=1,alpha = 0.8)

correlation = pd.DataFrame([s_list, soil_list]).T
correlation = correlation[np.isfinite(correlation).all(1)]   

plt.text(0.05,0.08,'R='+str(round(np.ma.corrcoef(correlation[correlation.columns[0]], correlation[correlation.columns[1]])[0,1],3)), fontsize=30)
plt.text(0.05,0.07,'N='+str(correlation.count()[0]), fontsize=30)
c19 = fig19.colorbar(image19, shrink=1, aspect=10,ticks=[0,0.2,0.4,0.6,0.8,1.0])
c19.ax.tick_params(labelsize=15)
c19.set_label('Fine Soil/ {AmSulf+FineSoil}', fontsize=22)
c19.set_ticklabels(['0','0.2','0.4','0.6','0.8','1.0'])    
plt.show()

#%%############################################################################################################
#######################                     Figure 20                          ################################
###############################################################################################################
################# x축 : FMF
################# y축 : SSA 440 
################# 컬러: 물질 비율, cmap=jet
################# ㅇㅇ

fig20, ax20 = plt.subplots(figsize = (12,10))
color = (f_all['BC PM2.5'])/(f_all['BC PM2.5']+f_all['Ammoniated Sulfate'])
image20 = ax20.scatter(f_all['FineModeFraction_500nm[eta]'], f_all['SSA_440'], c=color, cmap='jet',vmin=0,vmax=1, s=300, edgecolors='red', marker='o', zorder=2)
c20 = fig20.colorbar(image20,shrink=1, aspect=10, ticks=[0,0.2,0.4,0.6,0.8,1.0])
c20.ax.tick_params(labelsize=15)
c20.set_label('BC / {AmSulf+BC}', fontsize=22)          #f_all['Ammoniated Sulfate']+f_all['Ammonium Nitrate']+f_all['Sea Salt']+f_all['BC PM2.5']+f_all['Sea Salt']+f_all['Fine Soil']
c20.set_ticklabels(['0','0.2','0.4','0.6','0.8','1.0'])
n = f_all['SSA_440'].loc[(np.isnan(f_all['SSA_440'])==False) & (np.isnan(f_all['Fine_Mode_AOD_500nm[tau_f]'])==False) & (np.isnan(color)==False)].count()

plt.xlim(0,1)
plt.xticks(np.arange(0,1.01,0.2),fontsize=15)
plt.ylim(0.8,1)
plt.yticks(np.arange(0.8,1.01,0.04),fontsize=15)
plt.xlabel('FMF 500', fontsize=25)
plt.ylabel('SSA 440', fontsize=25)
plt.title('< FMF-SSA Classification All >', fontsize=20, fontweight='bold')
plt.text(0.1, 0.98,'N='+str(n), fontsize=30)

#%%############################################################################################################
#######################                     Figure 21                          ################################
###############################################################################################################
################# x축 : SAE
################# y축 : AAE 
################# 컬러: 물질그룹 (빨노초검)
################# ㅇㅇ

fig21, ax21 = plt.subplots(figsize = (10,10))

#Data Plotting
image21 = ax21.scatter(f_all['SAE'], f_all['AAE'], c=f_all['group'], s=300, edgecolors='red', marker='o', zorder=2)
plt.xlim(-0.5,2.51)
plt.xticks(np.arange(-0.5,2.501,0.5),fontsize=15)
plt.ylim(0,3)
plt.yticks(np.arange(0,3.01,1),fontsize=15)
plt.xlabel('SAE 440-870nm', fontsize=25)
plt.ylabel('AAE 440-870nm', fontsize=25)
plt.title('< Aerosol Type Classification All>', fontsize=20, fontweight='bold')
n = f_all['SAE'].loc[(np.isnan(f_all['SAE'])==False) & (np.isnan(f_all['AAE'])==False) & (f_all['group']!=None)].count()
plt.text(1.6, 2.7,'N='+str(n), fontsize=30, backgroundcolor='skyblue')

#draw lines
plt.plot([1,1],[0,1],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([-0.5,2.5],[1,1],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([-0.5,2.5],[1.5,1.5],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([1.5,1.5],[1.5,3],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([1.5,2.5],[1.5,1.5],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([1.5,2.5],[2,2],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([-0.5,0],[2,2],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([0,0],[2,3],'-',color='grey',linewidth=1,alpha = 0.8)
plt.plot([1,1.5],[1,1.5],'-',color='grey',linewidth=1,alpha = 0.8)
#type names
plt.text(-0.1,0.45,'Uncertain', fontsize=30)
plt.text(-0.28,0.33,'large and low absorbing', fontsize=18, color='grey')
plt.text(-0.4,2.43,'Dust', fontsize=30)
plt.text(1.63,0.45,' NA', fontsize=30)
plt.text(1.13,0.33,' small and low (non) absorbing', fontsize=18, color='grey')
plt.text(1.88,1.18,'BC', fontsize=30)
plt.text(1.7,1.06,'black carbon', fontsize=18, color='grey')
plt.text(1.7,1.68,'BC + BrC', fontsize=30)
plt.text(1.88,2.43,'BrC', fontsize=30)
plt.text(1.72,2.31,'brown carbon', fontsize=18, color='grey')
plt.text(-0.1,1.2,'Uncertain / BC', fontsize=30)
plt.text(0.3,2.2,'Dust / BC + BrC', fontsize=30)
#fmf criteria
plt.text(-0.1,1.06,'FMF<0.6', fontsize=12, color='blue')
plt.text(0.68,1.06,'FMF>0.6', fontsize=12, color='blue')
plt.text(-0.1,1.15,'--------------------------    --------', fontsize=16, color='blue')
plt.text(0.3,2.06,'FMF<0.4', fontsize=12, color='blue')
plt.text(0.75,2.06,'FMF>0.4', fontsize=12, color='blue')
plt.text(0.3,2.15,'------------     -------------------------', fontsize=16, color='blue')
plt.show()


#%%############################################################################################################
#######################                     Figure 22                          ################################
###############################################################################################################
################# 파이차트
################# SSA FMF 구역으로 분류된 그룹에 따라서 
################# 각 그룹이 어떤 광학유형(AAE-SAE)을 가지는지 비율 보여줌
################# 

f_color_list = ['black','red','orange','green']

for c in range (0,4):
    fig22, ax22 = plt.subplots(figsize = (10,10))
    f_color = globals()[f'f_{f_color_list[c]}']
    labels = ['Dust','BC','BC+BrC','NA','Uncertain']
    colors = ['gold','dimgray','tan','hotpink','skyblue']
    ratio = []
    l_ind = 0

    for l in labels:
        ratio.append(len(f_color.loc[f_color['type']==l]))
        if len(f_color.loc[f_color['type']==l]) == 0:
            labels[l_ind] = ''  #blank
        l_ind = l_ind+1

    ax22 = plt.pie(ratio, labels=labels, colors=colors, autopct = '%.1f%%', \
            wedgeprops = {'width' : 1, 'edgecolor' : 'grey', 'linewidth' : 3}, textprops={'size' : 30, 'color' : 'black'} )
    plt.title('Group Aerosol Types', fontsize=40, fontweight='bold',backgroundcolor=f_color_list[c])
    plt.show()

#%%############################################################################################################
#######################                     Figure 23                          ################################
###############################################################################################################
################# 막대그래프
################# SSA FMF 구역으로 분류된 그룹에 따라서 
################# 각 그룹이 가지는 필터유형 평균질량
################# 

fig23, ax23 = plt.subplots(figsize=(12,6))

bar_width = 0.1
bar_index = np.arange(4)

# 각 종류별로 3개 샵의 bar를 순서대로 나타내는 과정, 각 그래프는 0.25의 간격을 두고 그려짐
b1 = plt.bar(bar_index+bar_width, f_group['Ammoniated Sulfate'], bar_width, alpha=1, color='pink', label='AmSulf')
b2 = plt.bar(bar_index + 2*bar_width, f_group['Ammonium Nitrate'], bar_width, alpha=1, color='gold', label='AmNit')
b3 = plt.bar(bar_index + 3*bar_width, f_group['Sea Salt'], bar_width, alpha=1, color='skyblue', label='SeaSalt')
b4 = plt.bar(bar_index + 4*bar_width, f_group['Fine Soil'], bar_width, alpha=1, color='brown', label='FineSoil')
b5 = plt.bar(bar_index + 5*bar_width, f_group['BC PM2.5'], bar_width, alpha=1, color='black', label='BC')

# x축 위치를 정 가운데로 조정하고 x축의 텍스트를 year 정보와 매칭
plt.xticks(np.arange(bar_width, 4 + bar_width, 1)+0.2,  ['2) black','3) Green','1) Orange','4) Red'])
# x축, y축 이름 및 범례 설정
plt.xlabel('group', size = 13)
plt.ylabel('mean value', size = 13)
plt.legend()
plt.show()
# %%
