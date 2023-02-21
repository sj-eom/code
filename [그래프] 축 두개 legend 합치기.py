
두개 축 그리고
범례 2개 합치는 방법


fig, ax1 = plt.subplots(figsize = (15,5))   

line1 = ax1.plot(wd.index.strftime("%H"), wd, 'go', color='blue', label='wind direction')   
ax1.set_yticks(np.arange(0,365,90))
ax1.set_yticklabels(['0[N]', '90[E]', '180[S]', '270[W]', '360[N]'])
ax1.set_ylim(-5,365)
ax1.set_ylabel('wind direction [deg]', fontsize = 12)

ax2 = ax1.twinx()
line2 = ax2.plot(wd.index.strftime("%H"), ws, '-o', color='red', label='wind speed')
ax2.set_yticks(np.arange(0,15,2))
ax2.set_ylabel('wind speed [m/s]', fontsize = 12)

plt.xlim(-1,24)

ax1.set_xlabel('Datetime [KST]', fontsize = 12)
lines = line1 + line2
labels = labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right')
