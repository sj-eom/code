import glob
import mmap
import numpy as np


site = 'aeronet_yonsei'
# site = 'aeronet_unist'

path = 'C:/Users/PC/OneDrive - UNIST/*/*'

file_list = glob.glob(path+'*'+'.py')


for i in range (0, np.size(file_list)):
    with open(file_list[i]) as f:
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        if s.find(b'xlsx') != -1:
            print('True')
            print(file_list[i])
