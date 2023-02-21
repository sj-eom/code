
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


##############################################################################################
########select date########
#임의의 기간을 지정해주세요
date_start = '2005-01-01' 
date_end = '2007-12-31'

#월 지정 또는 전체 월 사용할지 선택해주세요
month_list = [1,2,3]  #연속되지 않아도 됩니다. 1,4,5 등도 가능함
# month_list = [1,2,3,4,5,6,7,8,9,10,11,12] 

#필요한 기간에 대해서만 1일 간격의 인덱스 생성
date = pd.date_range(start = date_start, end = date_end, freq='d')

#datetime 추출을 위해 데이터프레임으로 전환함
date = pd.DataFrame(date,columns=['time'])

#원하는 월 리스트만 뽑아서 리스트에 추가한다
date_list=[]
for r in month_list:
    date_list.append(date.loc[date['time'].dt.month==r])
    
#필요한 기간에 대한 리스트 생성하기
date_f = pd.concat(date_list)  #필요한 월에 대한 리스트만 일렬로 합침
date_f.index = date_f['time'] 
date_jul = pd.to_datetime(date_f.index, format = '%Y-%m-%d').strftime('%Y%j')  #줄리안데이로 전환함. strftime은 인덱스인 경우에만 사용가능하므로 date_f['time'] 대신 date_f.index 사용 

#최종적으로 선별된 날짜 내에서만 루프 돌려서 해당하는 자료 찾는다
file_list = []
for i in range (0, np.size(date_jul)):
    file_list.append(glob.glob(fpath + '*'+'A'+date_jul[i]+'*'+'*.hdf'))
                         
#빈 리스트 제외하고, 있는 파일명만 모아 통합하는 코드. 원하는 파일리스트 생성됨   
files =  np.concatenate(file_list)  
