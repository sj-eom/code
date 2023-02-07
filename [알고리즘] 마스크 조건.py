

operation = ma.masked_where(lat > lat_max, operation)
operation = ma.masked_where(lat < lat_min, operation)
operation = ma.masked_where(lon < lon_min, operation) 
operation = ma.masked_where(lon > lon_max, operation) 

operation = ma.masked_where(operation>2, operation) 
operation = ma.masked_where(operation<2, operation) 


mask = operation.mask #마스크 된 위치를 저장

xco2_quality_flag = ma.masked_where(mask, xco2_quality_flag) #마스크 위치 적용
xco2_quality_flag = ma.masked_where(xco2_quality_flag>0, xco2_quality_flag)
xco2_quality_flag = ma.masked_where(xco2_quality_flag<0, xco2_quality_flag)

mask2 = xco2_quality_flag.mask

operation = ma.masked_where(mask2, operation) 
