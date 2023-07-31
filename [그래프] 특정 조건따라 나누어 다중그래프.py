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


또는, 

#%% 그룹별로 나뉜 자료를 샘플링 기간에 맟줘 평균한 상관계수 #############################################################################
fig10, ax10 = plt.subplots(2,2, figsize = (16,16))
# 격자 여백 설정
plt.subplots_adjust(wspace = 0.5, hspace = 0.5)
colors = ['darkviolet','red','blue','white']
for c in colors:                            #컬러에 따른 그림 위치 정해준다
    if c == 'darkviolet':
        a, b = 0, 0   
    if c == 'red':
        a, b = 0, 1  
    if c == 'blue':
        a, b = 1, 0  
    if c == 'white':
        a, b = 1, 1  
    
    #나눠진 색깔 그룹을 다시 같은 샘플링 기간끼리 평균한다
    f_each_group = f[f['color']==c].groupby('Filter PM2.5 mass').mean() 
    #상관관계 계산
    f_ssa_list = f_each_group['SSA_1020']
    f_ratio_list = f_each_group['Ammoniated Sulfate']/f_each_group.index
    f_corr = pd.DataFrame([f_ssa_list, f_ratio_list]).T
    f_corr = f_corr.dropna(axis=0)
    #스캐터플롯 및 상관관계 같이 그리기
    ax10[a,b].scatter(f_each_group['SSA_1020'], f_each_group['Ammoniated Sulfate']/f_each_group.index, color=c, edgecolor='grey', s=150)
    ax10[a,b].text(0.86,0.9,'R='+str(round(np.ma.corrcoef(f_corr['SSA_1020'], f_corr[f_corr.columns[1]])[0,1],3)), fontsize=30)
    ax10[a,b].set_xlim(0.8,1) 
    ax10[a,b].set_ylim(0,1)
    ax10[a,b].set_xlabel('SSA 1020', fontsize=20) 
    ax10[a,b].set_ylabel('sulfate ratio', fontsize=20)
