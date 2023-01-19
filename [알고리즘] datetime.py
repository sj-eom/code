
##데이트타임으로 전환하기
data_aeronet['times'] = pd.to_datetime(data_aeronet['times'])
data_aeronet = data_aeronet.set_index('times')


##조건달기
###2021년 3월 이후의 데이터만 조회하기
df.loc[df["DateTime"] >= '2021-03']

###2021년 2월 13일 이후의 데이터만 조회하기
df[df["DateTime"] > '2021-02-13']

###특정월만 
df.loc[df["DateTime"].dt.month == 6]
