import pandas as pd
import glob
import os
import shutil

master_file_dir = 'C:\\Users\\eclass\\Desktop\\ECLASS\\'
data_directory = 'C:\\Users\\eclass\\Desktop\\ECLASS\\Fall2015Files_flat'

master_file = pd.read_csv(master_file_dir+'MasterFile.csv', skiprows=1)
print(master_file.columns)
pre_survey_ids = master_file.PreSurveyID
post_survey_ids = master_file.PostSurveyID
upper_lower_ids = master_file.Coursetype # [1,2,3] = intro, 4 = upper

os.chdir(data_directory)
os.makedirs('intro', exist_ok=True)
os.makedirs('upper', exist_ok=True)

for pre, post, type in zip(pre_survey_ids, post_survey_ids, upper_lower_ids):

    pre = glob.glob('*'+pre[3:]+'*')
    post = glob.glob('*'+post[3:]+'*')

    if type in [1,2,3]:
        if len(post) > 0:
            shutil.copy(os.getcwd()+pre[0], os.getcwd()+'\\intro')
            shutil.copy(os.getcwd()+post[0], os.getcwd()+'\\intro')
    elif type == 4:
        if len(post) > 0:
            shutil.copy(os.getcwd()+'\\'+pre[0], os.getcwd()+'\\upper')
            shutil.copy(os.getcwd()+'\\'+post[0], os.getcwd()+'\\upper')
