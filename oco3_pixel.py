import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import time
import glob
import pandas as pd
start = time.time()
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

path = '/home/data/satellite/OCO3/'
path = 'C:/Users/PC/OneDrive - UNIST/oco3/'
file_name = []
#extent_area = [124, 130, 34, 38]            #한반도
extent_area = [126, 127, 36.4, 37]          #안면도
# extent_area = [126, 127, 36.5, 37.5]
flist = glob.glob(path+'oco3_LtCO2*.nc4')
anmyeon = [36.5382, 126.3311]               #안면도 관측소


# for i in range(0, len(flist)):
for i in range(11,13):
    oper_list = []
        
    #netCDF4 호출
    f = Dataset(flist[i], 'r')
    print(flist[i])
    lon_min, lon_max, lat_min, lat_max = extent_area
    
    
    xco2 = f.variables['xco2'][:]
    lat = f.variables['latitude'][:]
    lon = f.variables['longitude'][:]
    time = f.variables['time'][:]
    date = f.variables['date'][:]
    lon_corner = f.variables['vertex_longitude'][:]
    lat_corner = f.variables['vertex_latitude'][:]
    operation = f['Sounding']['operation_mode'][:]
    qflag = f.variables['xco2_quality_flag'][:]
    
    xco2[qflag!=0] = np.nan     #qflag0이 아닌걸 nan값으로
    xco2[operation!=2] = np.nan #operation mode가 2가 아닌걸 nan으로
    
    f.close()   #netCDF4 파일 닫기
    
    #해당 도메인에 포함되는 픽셀 인덱스 추출
    a = lat < lat_max   #위도가 도메인 위도 최대값보다 작으면 True
    b = lat > lat_min   #위도가 도메인 위도 최소값보다 크면 True
    c = lon < lon_max   #경도가 도메인 경도 최대값보다 작으면 True
    d = lon > lon_min   #경도가 도메인 경도 최소값보다 크면 True

    test = a*b*c*d      #위경도가 모두 도메인 안에 들어가면 True
    
    ind_0_list = np.where(test == True)[0]    #True인 픽셀인덱스 추출
    
    #지도 호출
    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()), figsize=(12,8))
        
    ax.coastlines(resolution='10m')
    ax.set_extent(extent_area)
    
    gl = ax.gridlines( draw_labels= True,linewidth=0.1)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlocator = mticker.FixedLocator(np.arange(124,128,0.05))
    gl.ylocator = mticker.FixedLocator(np.arange(35.8, 37.4, 0.05))
    
    gl.xlines=False
    gl.ylines=False
    
    ax.set_title(flist[i])
    ax.add_feature(cfeature.LAND)
    
    xco2_min = np.nanmin(xco2[ind_0_list[:]])
    
    
    #추출한 픽셀 인덱스에 대해서 루프 실행
    # for check in range(320,460):
        
    for check in range(0,len(ind_0_list)):
        j = ind_0_list[check]
                                              #np.nanmin(xco2[ind_0_list[0:320]])
        #위경도 2x2 행렬 생성
        lat_target = np.zeros([2,2])*np.nan
        lon_target = np.zeros([2,2])*np.nan

        for x in range(0,2):
            for y in range(0,2):
                
                if x==0 and y==0:
                    ind = 0
                    
                elif x==0 and y==1:
                    ind = 1
                    
                elif x==1 and y==0:
                    ind = 3
                    
                elif x==1 and y==1:
                    ind = 2
                    
                lat_target[x,y] = lat_corner[j,ind]
                lon_target[x,y] = lon_corner[j,ind]
        
        #그림그릴 xco2값 호출
        xco2_target = xco2[j]
        
        #그림 그리기 -> 변수 차원 1x1로 만들어서 넣어줌
        al = ax.pcolormesh(lon_target, lat_target, np.reshape(np.array(xco2_target-xco2_min), (1,1)), transform=ccrs.PlateCarree(), cmap='viridis')
        # al = ax.pcolormesh(lon_target, lat_target, np.reshape(np.array(xco2_target), (1,1)), transform=ccrs.PlateCarree(), cmap='viridis')
        
        # al = ax.scatter(lon[j], lat[j], xco2_target, transform=ccrs.PlateCarree(), cmap='hsv')
        al.set_clim([0,10])
    #colorbar
    smaplegend = plt.colorbar(al, ticks=(np.arange(0,10, 0.2)))
    smaplegend.set_label('xco2 (ppm)', fontsize=15)
    #안면도 위치
    ax.scatter(anmyeon[1], anmyeon[0], c='r', s=200, marker='*')
    #그림 저장, 용량이 크면 dpi=200으로 변환
    fig.savefig('test1.png', dpi=500, bbox_inches='tight')
        


#%%
df = pd.DataFrame(file_name)
dff = np.array(file_name)
# df.to_csv('file_list_oco3.csv')
# np.savetxt("outnp.csv", dff, delimiter=",")
