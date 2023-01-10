
#########
order = ['Ammoniated Sulfate', 'Ammonium Nitrate', 'Sea Salt', 'Fine Soil', 'Equivalent BC PM2.5']
order_simple = ['sulfate','nitrate','seasalt','soil','bc']

for r in range (0, np.size(nan_data.index)):
    for n in range (0, 5):
        if nan_data[order[n]][r]/nan_data['major'][r] > 0.6:
            globals()['list_case_'+order_simple[n]].append(nan_data[r:r+1])
            
            if len(globals()['list_case_'+order_simple[n]])>0:
                
                globals()['case_'+order_simple[n]] = pd.concat(globals()['list_case_'+order_simple[n]])
                globals()['case_mean_'+order_simple[n]] = globals()['case_'+order_simple[n]].mean()
                case_data.append(globals()['case_mean_'+order_simple[n]])
    

case_data= pd.concat(case_data,axis=1).T
case_data = case_data.groupby(['number']).mean()

