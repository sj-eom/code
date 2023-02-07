

#리스트 내의 nan값 쉐이딩
ssa_list = np.ma.masked_invalid(ssa_list) 
ratio_list = np.ma.masked_invalid(ratio_list)


round(np.ma.corrcoef(ssa_list,ratio_list)[0,1],3)

#round = 반올림
