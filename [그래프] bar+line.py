#%%
fig3, ax3 = plt.subplots(figsize=(20,8))


bar_chart = ax3.bar(nan_data.index, nan_data['major'], color='#FBE5D6',label='major_chemical', width=5) 
bar_chart = ax3.bar(nan_data.index, nan_data['Filter PM2.5 mass']-nan_data['major'],\
                    bottom=nan_data['major'], color='#DEEBF7',label='Total PM2.5', width=5)



ax3.set_yticks(np.arange(0,101,20))
ax3.set_yticklabels(['0', '20', '40', '60', '80', '100'], fontsize=12)
ax3.legend(loc='upper left')
ax3.set_ylim(0,100)
ax3.set_ylabel('concentration (ug/m3)', fontsize = 11)


# # 
ax4 = ax3.twinx()

ax4.plot(nan_data['Fine Soil']/nan_data['major']*100, '-o', label='Fine Soil',color='brown')
ax4.plot(nan_data['Ammoniated Sulfate']/nan_data['major']*100, '-o', label='Ammoniated Sulfate', color='pink')
ax4.plot(nan_data['Ammonium Nitrate']/nan_data['major']*100, '-o', label='Ammonium Nitrate', color='gold')
ax4.plot(nan_data['Sea Salt']/nan_data['major']*100, '-o', label='Sea Salt', color='skyblue')
ax4.plot(nan_data['Equivalent BC PM2.5']/nan_data['major']*100, '-o', label='Equivalent BC PM2.5', color='grey')
ax4.legend()
ax4.set_ylabel('major ratio [%]')

ax3.set_xlabel('Time')
