'''2023.03.27 Sujin Eom'''
#%%
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import glob
from pyhdf.SD import SD, SDC
pd.set_option('mode.chained_assignment',  None) # 경고 off
#%%
path = 'C:/Users/PC/OneDrive - UNIST/'
site_list = ['busan','daegu','daejeon','seoul','ulsan']
year = 2021

for site in site_list:
    globals()['day_'+site] = []

for site in site_list:
    day_list = []
    
    for jul in range (1,366):
        ec_daily_list = []
    
        c = format(jul, '03') # '03' : 숫자 형식을 바꿈 ex ) 3>003, 15>015
        d = str(year) + str(c)
        d_cal = datetime.strptime(d,'%Y%j').strftime('%Y-%m-%d') #2012003 > 0103 년+줄리안 > 월+일
        file = glob.glob(path+'*'+d_cal+'T'+'*.hdf')
        day_list.append(d_cal)
        print(d_cal, site)
        #만약에 해당 날짜 파일이 아예 없다면
        if np.size(file) == 0:
            globals()['day_'+site].append(np.nan)
        #있다면
        else:
            for r in range (0,np.size(file)):
                f = SD(file[r], SDC.READ)
                ec = f.select('Extinction_Coefficient_532')[:]
                lat = f.select('Latitude')[:]
                lon = f.select('Longitude')[:]
        
                ec[ec == -9999] = np.nan
                ec = ec[:,382:390] #heingt 0~0.5km
                lat = lat[:,1] #가운데 점만 사용
                lon = lon[:,1]
                ec_mean = np.nanmean(ec,axis=1)
                f = pd.DataFrame(np.vstack((lat, lon, ec_mean)).T, columns=['lat','lon','ec']).astype('float')
                ec_daily_list.append(f)

            ec_daily_stack = pd.DataFrame(np.vstack(ec_daily_list), columns=['lat','lon','ec'])
            # print(ec_daily_stack.ec.count(), site)
            globals()['data_'+site] = pd.read_table(path + 'total 2021 pm csv/total 2021 '+site+'.csv', sep=','
                                                , names = ['date','pm10','pm25','lat','lon'],
                                                skiprows = 1, index_col=0)
            deg_lat, deg_lon = [globals()['data_'+site].lat[0], globals()['data_'+site].lon[0]]
            deg_lim = 1    
            globals()['data_'+site+'_daily'] = ec_daily_stack[(ec_daily_stack['lat'] < deg_lat + deg_lim) 
                                                & (ec_daily_stack['lat'] > deg_lat - deg_lim)
                                                & (ec_daily_stack['lon'] < deg_lon + deg_lim) 
                                                & (ec_daily_stack['lon'] > deg_lon - deg_lim)]
            globals()['day_'+site].append(globals()['data_'+site+'_daily'].ec.mean()) 
        
    
day_total = pd.DataFrame((day_busan, day_daegu, day_daejeon, day_seoul, day_ulsan)).T
day_total.index = day_list
day_total.columns = site_list

for site in site_list:
    
    globals()['data_join_'+site] = globals()['data_'+site].join(day_total[site])
    del globals()['data_join_'+site]['lat'] 
    del globals()['data_join_'+site]['lon']
    globals()['data_join_'+site].rename(columns = {site:'ec'}, inplace=True)
    # globals()['data_'+site].to_csv(path+'total 2021 pm csv/calipso_pm_'+site+'.csv')
