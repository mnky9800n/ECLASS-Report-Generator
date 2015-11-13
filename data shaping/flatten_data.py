import os
import glob
import shutil

top_dir = 'C:\\Users\\eclass\\Desktop\\ECLASS\\'
data_directory = 'C:\\Users\\eclass\\Desktop\\ECLASS\\Fall2015Files'


#make a new directory for flat stuff
flat_dir = top_dir+data_directory.split('\\')[-1]+'_flat'
os.makedirs(flat_dir, exist_ok=True)

dirs = [d for d in os.walk(data_directory)]

for dir in dirs[1:]:
    directory = dir[0]
    files = dir[2]
    for f in files:
        if 'names' in f:
            pass
        else:
            shutil.copy(directory+'\\'+f,flat_dir)
