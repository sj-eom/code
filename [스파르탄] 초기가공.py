

for r in list_spartan.index:
# r = list_spartan.Site_Code[0]
# r = 'ILHA'
    def filter_station (file_name):
    # file_name = f'FilterBased_ReconstrPM25_{site.inform[0]}.csv'
    # file_name = f'FilterBased_ReconstrPM25_{list_spartan.Site_Code[r]}.csv'
        path = '/home/sjeom/data/SPARTAN/all/'
        spartan_25 = path+file_name 

        ################기초 데이터 생성-날짜인덱스####################################
        data_org = pd.read_csv(spartan_25, skiprows=1, delimiter=',')
        data = data_org.copy()                                   
        df_groupby = data.groupby('Parameter_Name')

        check = 0
        for var in list(dict.fromkeys(data['Parameter_Name'])) : #나타난 순서 기준으로 중복 제거해서 나열하기
            df_var = df_groupby.get_group(var)
            
            df_var['start_date'] = df_var.Start_Year_local.astype(str)+df_var.Start_Month_local.astype(str).str.zfill(2)+df_var.Start_Day_local.astype(str).str.zfill(2)#+df_var[' Start_hour_local'].astype(str).str.zfill(2)
            df_var['start_date'] = pd.to_datetime(df_var.start_date, format='%Y%m%d')
            df_var['end_date'] = df_var.End_Year_local.astype(str)+df_var.End_Month_local.astype(str).str.zfill(2)+df_var.End_Day_local.astype(str).str.zfill(2)#+df_var['End_hour_local'].astype(str).str.zfill(2)
            df_var['end_date'] = pd.to_datetime(df_var.end_date, format='%Y%m%d')

            df_var.rename(columns={'Value':var}, inplace=True)
            df_var = df_var[[var, 'start_date', 'end_date', 'Filter_ID']]

            if check == 0:
                merge_df = df_var
                check+=1
            else:
                merge_df = pd.merge(merge_df, df_var, how='outer', on=['start_date','end_date','Filter_ID'])
        merge_df.set_index('start_date', inplace=True)
        merge_df['start_date'] = merge_df.index
        return merge_df
    df_filter = filter_station (f'FilterBased_ReconstrPM25_{list_spartan.Site_Code[r]}.csv')  #필터자료 정렬
