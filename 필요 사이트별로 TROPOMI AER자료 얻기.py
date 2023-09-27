#%%
import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import time
import glob
import pandas as pd
import datetime
from os import path
start = time.time()
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

#%% File Path ########################################################################################

path = '/data01/satellite/TROPOMI/TROPOMAER/'
list_spartan = pd.read_table('/home/sjeom/result/site_list_spartan.csv', delimiter=',',usecols=[1,2,3,4,5])

#데이터 입력할 판 짜기
df_ssa = pd.DataFrame(columns=list_spartan.Site_Code, index=pd.date_range(start = '2018-01-01', end = '2023-12-31', freq='1d', name='times'))
df_aod = pd.DataFrame(columns=list_spartan.Site_Code, index=pd.date_range(start = '2018-01-01', end = '2023-12-31', freq='1d', name='times'))
df_uvai = pd.DataFrame(columns=list_spartan.Site_Code, index=pd.date_range(start = '2018-01-01', end = '2023-12-31', freq='1d', name='times'))

#%% Calculating ########################################################################################
#  파일 이름 :  TROPOMI-Sentinel-5P_L2-TROPOMAER_2018m0430t052420-o02821_v01-2021m0802t103012.nc
for year in range (2018,2021):
    for jul in range (1,367):
        
        for l in list_spartan.Site_Code: #일별 리스트 만들기
            globals()[l+'_ssa'+str(year)+str(jul)] = []
            globals()[l+'_aod'+str(year)+str(jul)] = []
            globals()[l+'_uvai'+str(year)+str(jul)] = []

            globals()[l+'_lat'+str(year)+str(jul)] = []
            globals()[l+'_lon'+str(year)+str(jul)] = []
        
        c = format(jul, '03') # '03' : 숫자 형식을 바꿈 ex ) 3>003, 15>015
        d = str(year) + str(c)
        print(d)
        
        d_tro = datetime.datetime.strptime(d,'%Y%j').strftime('%m%d') #2012003 > 0103 년+줄리안 > 월+일
        d_basic = str(year)+'-'+str(d_tro)[0:2]+'-'+str(d_tro)[2:4]  #2012-01-01 형식
        tro = glob.glob(path+'*TROPOMAER_'+str(year)+'m'+d_tro+'*.nc')
        
        if len(tro) == 0: #일자에 자료가 있는 경우
            continue
        else:
            for i in range(0, np.size(tro)):
            # for i in range(11,13):
                #netCDF4 호출
                f = Dataset(tro[i], 'r')
                print(tro[i])
                # lon_min, lon_max, lat_min, lat_max = extent_area
                
                # 0: 355, 1: 388, 2: 500
                ssa_388 = f.groups['SCIDATA'].variables['FinalAerosolSingleScattAlb'][:,:,1]
                # ssa_500 = f.groups['SCIDATA'].variables['FinalAerosolSingleScattAlb'][:,:,2]
                lat = f.groups['GEODATA'].variables['latitude'][:]
                lon = f.groups['GEODATA'].variables['longitude'][:]
                time = f.groups['GEODATA'].variables['time'][:]
                # aod_388 = f.groups['SCIDATA'].variables['FinalAerosolOpticalDepth'][:,:,1]
                aod_500 = f.groups['SCIDATA'].variables['FinalAerosolOpticalDepth'][:,:,2]
                uvai = f.groups['SCIDATA'].variables['UVAerosolIndex'][:]

            
                for m in range (0, np.size(list_spartan.index)):
                    deg = 0.25 #위경도 제한범위 두기
                    x, y = np.where((lat > list_spartan.Latitude[m]-deg) & (lat < list_spartan.Latitude[m]+deg)
                                    & (lon > list_spartan.Longitude[m]-deg) & (lon < list_spartan.Longitude[m]+deg))
                    # print(list_spartan.Site_Code[m], ssa_388[x,y])
                    globals()[list_spartan.Site_Code[m]+'_ssa'+str(year)+str(jul)].append(ssa_388[x,y])
                    globals()[list_spartan.Site_Code[m]+'_aod'+str(year)+str(jul)].append(aod_500[x,y])
                    globals()[list_spartan.Site_Code[m]+'_uvai'+str(year)+str(jul)].append(uvai[x,y])


        for l_list in list_spartan.Site_Code: #일별 리스트 만들기
            globals()[l_list+'_mean_ssa'+str(year)+str(jul)] = np.nanmean([y_ind for x_ind in globals()[l_list+'_ssa'+str(year)+str(jul)] for y_ind in x_ind])
            globals()[l_list+'_mean_aod'+str(year)+str(jul)] = np.nanmean([y_ind for x_ind in globals()[l_list+'_aod'+str(year)+str(jul)] for y_ind in x_ind])
            globals()[l_list+'_mean_uvai'+str(year)+str(jul)] = np.nanmean([y_ind for x_ind in globals()[l_list+'_uvai'+str(year)+str(jul)] for y_ind in x_ind])

            print(d_basic)
            date_d = datetime.datetime.strptime(d_basic,'%Y-%m-%d')

            df_ssa[l_list].loc[date_d.strftime('%Y-%m-%d')] = globals()[l_list+'_mean_ssa'+str(year)+str(jul)]
            df_aod[l_list].loc[date_d.strftime('%Y-%m-%d')] = globals()[l_list+'_mean_aod'+str(year)+str(jul)]
            df_uvai[l_list].loc[date_d.strftime('%Y-%m-%d')] = globals()[l_list+'_mean_uvai'+str(year)+str(jul)]

# Saving ########################################################################################
df_ssa.to_csv(f'/home/sjeom/result/tro_ssa_388_+-{deg}.csv')
df_aod.to_csv(f'/home/sjeom/result/tro_aod_500_+-{deg}.csv')
df_uvai.to_csv(f'/home/sjeom/result/tro_uvai_+-{deg}.csv')
