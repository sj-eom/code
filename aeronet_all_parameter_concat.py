# path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_seoul/20190101_20221231_Seoul_SNU' #서울대 자료
# path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_yonsei/20190101_20221231_Yonsei_University' #연세대 자료
path = 'C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_unist/20200101_20221231_KORUS_UNIST_Ulsan' #유니스트 자료

data_aod = path+'.lev15'
data_ssa = path+'.ssa'
data_fmf = path+'.ONEILL_lev15'
data_aae = path+'.tab'
data_eae = path+'.aod'
data_dep = path+'.lid' 
data_siz = path+'.siz' 

#%% FILTERING
parameter = ['aod', 'fmf', 'ssa', 'aae', 'eae', 'dep', 'siz']

for j in range (0, np.size(parameter)):
    ###############bring data######################################
    globals()['data_'+str(parameter[j])] = pd.read_table(globals()['data_'+str(parameter[j])],sep=",", skiprows=6)
    ###############aod original data###############################
    if str(parameter[j]) == 'aod':
        data_org = globals()['data_'+str(parameter[j])].copy()
    ###############change column name of fmf#######################
    if str(parameter[j]) == 'fmf':
        globals()['data_'+str(parameter[j])].rename(columns={'Date_(dd:mm:yyyy)':'Date(dd:mm:yyyy)'}, inplace=True)
    ###############remove -999 and set datetime index##############
    globals()['data_'+str(parameter[j])] = globals()['data_'+str(parameter[j])].replace(to_replace = -999, value = np.nan)
    globals()['data_'+str(parameter[j])]['times'] = pd.to_datetime(globals()['data_'+str(parameter[j])]['Date(dd:mm:yyyy)'], format = "%d:%m:%Y")
    globals()['data_'+str(parameter[j])] = globals()['data_'+str(parameter[j])].set_index('times')
    
#%% ARRANGE
data_AOD = data_aod[['AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm','AOD_1020nm']] 
data_FMF = data_fmf[['FineModeFraction_500nm[eta]','Total_AOD_500nm[tau_a]','Fine_Mode_AOD_500nm[tau_f]']] #to compare with 550 and 500
data_SSA = data_ssa[['Single_Scattering_Albedo[440nm]','Single_Scattering_Albedo[675nm]','Single_Scattering_Albedo[870nm]','Single_Scattering_Albedo[1020nm]']]
data_AAE = data_aae[['Absorption_AOD[440nm]','Absorption_AOD[870nm]','Absorption_Angstrom_Exponent_440-870nm']]
data_EAE = data_eae[['AOD_Extinction-Total[440nm]','AOD_Extinction-Total[870nm]','Extinction_Angstrom_Exponent_440-870nm-Total']]
data_DEP = data_dep[['Lidar_Ratio[440nm]','Depolarization_Ratio[440nm]']]
data_SIZ = data_siz[data_siz.columns[5:27]]
############reset index to merge#################
parameter_c = ['AOD', 'FMF', 'SSA', 'AAE', 'EAE', 'DEP', 'SIZ']
for k in range (0, np.size(parameter_c)):
    globals()['data_'+str(parameter_c[k])] = globals()['data_'+str(parameter_c[k])].reset_index()    

#%% MERGE
time_index = pd.date_range(start = '2019-01-01', end = '2022-12-31', freq='1d', name='times')
time = pd.DataFrame(time_index)
merge_1 = pd.merge(time, data_AOD, how='outer')
merge_2 = pd.merge(merge_1, data_FMF, how='outer')
merge_3 = pd.merge(merge_2, data_SSA, how='outer')
merge_4 = pd.merge(merge_3, data_AAE, how='outer')
merge_5 = pd.merge(merge_4, data_EAE, how='outer')
merge_6 = pd.merge(merge_5, data_DEP, how='outer')
data = pd.merge(merge_6, data_SIZ, how='outer')
data = data.set_index('times')

#%% CALCULATE 550 AND SAE
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

#%% REARRANGE TO CLASSIFY
#필요한 열 추출
data_ae = data.copy()
data = data[['AOD_440nm','AOD_550','FMF_550','SSA_440']]



#%%

aero = data_ae.copy()
siz = data_ae.copy()
siz = siz[siz.columns[20:42]]
# siz.to_csv('C:/Users/PC/OneDrive - UNIST/SPARTAN/aeronet_seoul/seoul_aeronet+siz.csv')
# aero.to_csv(path+'_full_parameter.csv')
