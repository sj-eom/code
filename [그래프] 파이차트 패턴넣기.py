

f_color_list = ['black','red','gold','skyblue']

for c in range (0,4):
    fig22, ax22 = plt.subplots(figsize = (10,10))
    f_color = globals()[f'f_{f_color_list[c]}']
    labels = ['Dust','BC','BC+BrC','NA','Uncertain']
    colors = ['gold','dimgray','tan','hotpink','skyblue']
    hatch = ['-','/O','x','.','']
    ratio = []
    l_ind = 0

    for l in labels:
        ratio.append(len(f_color.loc[f_color['type']==l]))
        if len(f_color.loc[f_color['type']==l]) == 0:
            labels[l_ind] = ''  #blank
        l_ind = l_ind+1

    ax22 = plt.pie(ratio, labels=labels, colors=colors, autopct = '%.1f%%', \
            wedgeprops = {'width' : 1, 'edgecolor' : 'grey', 'linewidth' : 3}, textprops={'size' : 30, 'color' : 'black'} )
    patches = ax22[0]
    for h in range (0, 5):

        patches[h].set_hatch(hatch[h])

    plt.title('Group Aerosol Types', fontsize=40, fontweight='bold',backgroundcolor=f_color_list[c])
    plt.show()
