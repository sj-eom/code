# %%# 늘려진 그룹 4가지로 나눠서 색깔별로 플롯해보기 ############################################################################
fig4, ax4 = plt.subplots(2,2, figsize = (16,16))
# 격자 여백 설정
plt.subplots_adjust(wspace = 0.5, hspace = 0.5)

for j in range (0, np.size(f.index)):
    if f['color'].astype('str')[j] != 'nan': #컬러 칼럼을 str 타입으로 바꾼 후, 해당 행이 nan이 아니라면
        #컬러를 인수로 넣어 4개 그룹별로 값 할당한다
        class Color:
            def __init__(self, color):
                if color == 'white':
                    self.color = [1, 1, 'low AOD low ext_r']
                if color == 'blue':
                    self.color = [1, 0, 'low AOD high ext_r']
                if color == 'red':
                    self.color = [0, 1, 'high AOD low ext_r']
                if color == 'darkviolet':
                    self.color = [0, 0, 'high AOD high ext_r']
        Color = Color(f['color'][j])
    
        #색깔과 위치 지정하기
        a, b = Color.color[0], Color.color[1]
        title = Color.color[2]

        ax4[a,b].scatter(f['SSA_1020'][j],f['Ammoniated Sulfate'][j]/f['Filter PM2.5 mass'][j],\
                c=f['color'][j], s=150, marker='o', edgecolor='grey',zorder=2, alpha=0.8)
        ax4[a,b].set_title(title, fontsize=20)
        ax4[a,b].set_xlim(0.8,1)
        ax4[a,b].set_ylim(0,1)
        ax4[a,b].set_xlabel('SSA 1020', fontsize=20)
        ax4[a,b].set_ylabel('sulfate ratio', fontsize=20)
    else:
        continue


