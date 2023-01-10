#지도 호출 / for OCO3
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

