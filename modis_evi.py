'''2023.02.21 sujin'''
#%%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
from pyhdf.SD import SD, SDC
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import *

#%%
fpath = 'C:/Users/PC/OneDrive - UNIST/MODIS/'

#%%
########select date########
#임의의 기간을 지정해주세요
date_start = '2005-01-01' 
date_end = '2007-12-31'

#월 지정 또는 전체 월 사용할지 선택해주세요
month_list = [1,2,3]  #연속되지 않아도 됩니다. 1,4,5 등도 가능함
# month_list = [1,2,3,4,5,6,7,8,9,10,11,12] 

#%%

#필요한 기간에 대해서만 1일 간격의 인덱스 생성
date = pd.date_range(start = date_start, end = date_end, freq='d')

#datetime 추출을 위해 데이터프레임으로 전환함
date = pd.DataFrame(date,columns=['time'])

#원하는 월 리스트만 뽑아서 리스트에 추가한다
date_list=[]
for r in month_list:
    date_list.append(date.loc[date['time'].dt.month==r])
    
#필요한 기간에 대한 리스트 생성하기
date_f = pd.concat(date_list)  #필요한 월에 대한 리스트만 일렬로 합침
date_f.index = date_f['time'] 
date_jul = pd.to_datetime(date_f.index, format = '%Y-%m-%d').strftime('%Y%j')  #줄리안데이로 전환함. strftime은 인덱스인 경우에만 사용가능하므로 date_f['time'] 대신 date_f.index 사용 

#%%

#최종적으로 선별된 날짜 내에서만 루프 돌려서 해당하는 자료 찾는다
file_list = []
for i in range (0, np.size(date_jul)):
    file_list.append(glob.glob(fpath + '*'+'A'+date_jul[i]+'*'+'*.hdf'))
                         
#빈 리스트 제외하고, 있는 파일명만 모아 통합하는 코드. 원하는 파일리스트 생성됨   
files =  np.concatenate(file_list)  

#%%
varname = 'CMG 0.05 Deg Monthly EVI'

#최종 선정된 파일들만 가지고 루프 돌린다
evi_list = []
for j in range (0, len(files)):
    file = SD(files[j], SDC.READ)
    sds = file.select(varname)
    sds_att = sds.attributes()
    for key, value in sds_att.items():
        if key == 'valid_range':
            valrange = np.asarray(value)
        if key == '_FillValue':
     	    fillval = value
        if key == 'scale_factor':
     	    scalefac = value
    
    ## missing data handling
    dat = sds.get().astype(np.float32)
           
    # 이부분 조건을 바꿔서 원하는 기간선택
    idx = np.where((dat == fillval)|(dat < valrange[0])|(dat > valrange[1]))
    dat[idx] = np.nan   
    evi = dat / scalefac

    #루프 돌리면서 파일 리스트 마다의 evi를 하나씩 챙김
    evi_list.append(evi)     

#모아진 evi를 3차원 어레이로 합친뒤 같은 위치에 따라 평균함 (따라서 루프밖에서 수행됨)
evi_mean = np.nanmean(np.array(evi_list),axis=0)  
    
#%%
#---------------------------------------
# GRID INFO
#---------------------------------------
nlon = 7200
nlat = 3600

#lons = np.linspace(-180,180,nlon)
lons = np.arange(-180,180,0.05)
lats = np.arange(90,-90,-0.05)

lon2d, lat2d = np.meshgrid(lons, lats)

#---------------------------------------
# DRAW MAP
#---------------------------------------

#그림사이즈 지정
fig = plt.figure(figsize=(12,8))
plt.ion()

ax = plt.axes(projection = ccrs.PlateCarree())
ax.set_global()


# 평균된 evi 사용해 플로팅
# vmin,max로 컬러바 최대 최소값 지정하시면 됩니다
al = ax.pcolormesh(lon2d, lat2d, evi_mean, vmin = -0.3, vmax = 0.5)
ax.coastlines()

#그리고 싶은 위경도범위 지정 옵션
# ax.set_extent([120,135,30,45]) #우리나라

g = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
g.right_labels = False
g.top_labels = False
g.xformatter = LONGITUDE_FORMATTER
g.yformatter = LATITUDE_FORMATTER

#컬러바 생성, arange로 컬러바 간격 지정함
smaplegend = plt.colorbar(al, ticks=np.arange(-0.3,0.51,0.1),shrink=0.6)
smaplegend.set_label('EVI', fontsize=15)

#지정한 자료 기간과 월이 보이도록 제목설정할수있음
plt.title(date_start+' ~ '+date_end+' / month='+str(month_list))
plt.show()
