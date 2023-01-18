

fig, ax = plt.subplots(figsize=(12,6))
bar_width = 0.25

# 
bar_index = np.arange(5)

# 각 종류별로 3개 샵의 bar를 순서대로 나타내는 과정, 각 그래프는 0.25의 간격을 두고 그려짐
b1 = plt.bar(bar_index, type_mean[1.0], bar_width, alpha=0.4, color='pink', label='sulfate')

b4 = plt.bar(bar_index + bar_width, type_mean[4.0], bar_width, alpha=0.4, color='brown', label='soil')

b5 = plt.bar(bar_index + 2*bar_width, type_mean[5.0], bar_width, alpha=0.4, color='grey', label='BC')


# x축 위치를 정 가운데로 조정하고 x축의 텍스트를 year 정보와 매칭
plt.xticks(np.arange(bar_width, 5 + bar_width, 1), ['aod','fmf','ssa','aae','dep'])

# x축, y축 이름 및 범례 설정
plt.xlabel('parameter', size = 13)
plt.ylabel('mean value', size = 13)
plt.title('mean by 1st type')
plt.legend()
plt.show()
