
fig3, ax3 = plt.subplots(figsize = (20,8))

#Filter PM2.5 mass
# plt.plot(f['Filter PM2.5 mass'],color='black', linewidth=0.8, linestyle='--', label=f.columns[0], marker='o' ) 

bar_chart = ax3.bar(f.index, f['Filter PM2.5 mass'],bottom=0
                    , color='black',label='total', width=8, alpha=0.5)

bar_chart = ax3.bar(f.index, f['Ammoniated Sulfate'], color='hotpink',label='Ammoniated Sulfate',\
                    width=8) 

bar_chart = ax3.bar(f.index, f['Ammonium Nitrate'],bottom=f['Ammoniated Sulfate'], \
                    color='gold',label='Ammonium Nitrate', width=8)
    
bar_chart = ax3.bar(f.index, f['Sea Salt'],bottom=f['Ammoniated Sulfate']+f['Ammonium Nitrate']\
                    , color='skyblue',label='Sea Salt', width=8)

bar_chart = ax3.bar(f.index, f['Fine Soil'],bottom=f['Ammoniated Sulfate']+f['Ammonium Nitrate']\
                    +f['Sea Salt'], color='brown',label='Fine Soil', width=8)

bar_chart = ax3.bar(f.index, f['BC PM2.5'],bottom=f['Ammoniated Sulfate']+\
                    f['Ammonium Nitrate']+f['Sea Salt']+f['Fine Soil']
                    , color='black',label='Black Carbon', width=8)

bar_chart = ax3.bar(f.index, f['Trace Element Oxides'],bottom=f['Ammoniated Sulfate']+\
                    f['Ammonium Nitrate']+f['Sea Salt']+f['Fine Soil']+f['BC PM2.5']
                    , color='green',label='Trace element', width=8)

bar_chart = ax3.bar(f.index, f['Residual Matter'],bottom=f['Ammoniated Sulfate']+\
                    f['Ammonium Nitrate']+f['Sea Salt']+f['Fine Soil']+f['BC PM2.5']\
                        +f['Trace Element Oxides']\
                    , color='olive',label='Residual Matter', width=8)



ax3.set_yticks([0,10,20,30,40])
ax3.set_yticklabels(['0', '10', '20', '30','40'], fontsize=20)
# ax3.legend(loc='upper left')
ax3.set_ylim(0,40.1)
ax3.set_ylabel('concentration (ug/m3)', fontsize = 20)
 
ax4 = ax3.twinx()
ax4.plot(day_list, max_aod, color='red', linewidth=0.8, linestyle='--', label='max AOD', marker='o' )
ax4.plot(day_list, mean_aod, color='black', linewidth=0.8, linestyle='--', label='mean AOD', marker='o' )
ax4.set_ylabel('AOD550nm', fontsize = 20)

ax3.set_xlabel('Time')

plt.ylim([-3,3])
plt.yticks([0,0.5,1,1.5,2.0])
plt.xticks(rotation=45)
plt.xlim(['2019-04-01'],['2022-09-01'])
        
