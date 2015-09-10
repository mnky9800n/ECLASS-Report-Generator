# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 14:00:29 2013

@author: Takako
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jan 04 12:23:40 2013

@author: Ben
"""

import numpy as np 
import pandas as p
import pylab as py
import scipy.stats as stats
import os
import datetime as dt
import matplotlib.pyplot as plt
from scipy.misc import factorial, comb
from scipy.optimize import leastsq
from scipy.stats.stats import pearsonr
from scipy.special import gammaln
from matplotlib.patches import Ellipse
import matplotlib.gridspec as gridspec
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable

import Import_Sp15 as Import

#Needed to switch base directory for dropbox and to 
#change between \\ and / for directories
_user = 'Takako' #Can be changed as an input to the initialize data function

_common_directory = ''
_graph_directory = ''
_table_directory = ''
_data_directory = ''

#Header Files
_header_IDs_file = 'header_IDs.csv'                 #IDs 
_pre_header_file = 'header_pre_results.csv'         #Pre results
_post_header_file = 'header_post_results.csv'       #Post results
_class_meta_data_file = 'Class_Meta_data.csv'       #class meta data

header_pre = [0]
header_post = [0]
q_guide = [0]
data = [0]
data_raw = [0]
data_raw_nodups = [0]  # raw data with duplicates removed (but not matched).
course_data = [0]

#figure specifications
fig_size = (6,6)
font_size = 14
dots_per_inch = 300


def initialize_data_clean_qualtrics(data_dir,pre_file, post_file, reload_data=True) :
    """
    Cleans up the data from the basic initialize_data function.

    reload_data : if True, then data is assumed to have updated, and matching is redone
                    (which can be slow for large data sets)

    """
    global data, header_pre, header_post, data_raw, data_raw_nodups
    data_dict = Import.initialize_data_Qualtrics(data_dir,pre_file,post_file)

    # Unpack all of the information from the Import file
    data = data_dict['data']
    header_pre = data_dict['header_pre']
    header_post = data_dict['header_post']
    #filepaths = data_dict['filepaths']

    data_raw = data.copy() #keep a copy of the original data set

    #remove empty rows (no answers to the Likert scale questions)
    to_drop = drop_empty_rows(data)                             # get the rows to drop
    data = data.drop(to_drop)

    data = data_query(data,q40a=4,q40b=4)  # only keep responses where students answered test questions right

    data.insert(loc=0, column = 'SID_matched', value = 0)
    #match and further clean the raw data
    if reload_data == True:
        data = remove_duplicates(data)
        data_raw_nodups = data.copy()  # save a copy with duplicates removed, since it is a very slow step.
        data_raw_nodups = data_query(data_raw_nodups,q40a=4,q40b=4)
        data = make_matched_subset_fuzzy(data)

def initialize_data_clean(semester, year, user, reload_data=True) :
    """
    Cleans up the data from the basic initialize_data function.

    reload_data : if True, then data is assumed to have updated, and matching is redone
                    (which can be slow for large data sets)

    """
    global data, header_pre, header_post, data_raw
    data_dict = Import.initialize_data(semester,year,user)

    # Unpack all of the information from the Import file
    data = data_dict['data']
    # ty_course_data = data_dict['course_data']
    header_pre = data_dict['header_pre']
    header_post = data_dict['header_post']
    #filepaths = data_dict['filepaths']

    data_raw = data.copy() #keep a copy of the original data set

    #remove empty rows (no answers to the Likert scale questions)
    to_drop = drop_empty_rows(data)                             # get the rows to drop
    data = data.drop(to_drop)

    data.insert(loc=0, column = 'SID_matched', value = 0)
    #match and further clean the raw data
    if reload_data == True:
        data = remove_duplicates(data)
        data = make_matched_subset_fuzzy(data)

def initialize_data(user='Takako',reloading=False):
    """
    User can be 'Takako' or 'Ben' to adjust the directory structure
    """    
    global _user, data, data_raw, header_pre, header_post, q_guide, categories, _common_directory, \
            _graph_directory, _table_directory, _data_directory, course_data, filepaths

    _user = user
    #Set Ben directory
    if _user == 'Ben':
        _common_directory = 'C:\\SugarSync\\Ben\\RIT\\Research\\E-CLASS\\Python Report Generation\\Spring 2015\\'
        #_common_directory = 'C:\\Users\\Ben\\Dropbox\\E-CLASS\\Analysis\\ALL_E-CLASS\\Summer 2013\\'
        _graph_directory = _common_directory + "graphs\\"
        _table_directory = _common_directory + "tables\\"
        _data_directory = _common_directory + 'Qualtrics Data\\'
    #Set Takako directory
    elif _user == 'Takako' :
        _common_directory = '/Users/Takako/Dropbox/E-CLASS/Analysis/ALL_E-CLASS/Summer 2013/'
        _graph_directory = _common_directory + "graphs/"
        _table_directory = _common_directory + "tables/"
        _data_directory = _common_directory + 'Clean data/'
    
    term_year = [('Fall','2012'),('Spring', '2013')]    
    
    filepaths={}
    data_list=[]
    course_data_list=[]
    header_pre={}
    header_post={}
        
    for termyear in term_year:
        termyearlabel = termyear[0][0:2]+termyear[1][2:4]
        data_dict = Import.initialize_data(termyear[0],termyear[1],_user)
        
        #Unpack all of the information from the Import file
        ty_data = data_dict['data']
        ty_course_data = data_dict['course_data']
        ty_header_pre = data_dict['header_pre']
        ty_header_post = data_dict['header_post']
        ty_filepaths = data_dict['filepaths']
        
        ty = [ty_data, ty_course_data]
        #Add what semester/year
        for ty_items in ty:
            ty_items.insert(loc=0, column='Semester', value = termyear[0])
            ty_items.insert(loc=1, column='Year', value = termyear[1])
        
        data_list.append(ty_data)
        course_data_list.append(ty_course_data)
        
        header_pre[termyearlabel]=ty_header_pre
        header_post[termyearlabel]=ty_header_post
        filepaths[termyearlabel]=ty_filepaths
    
    #Bringing it all together
    course_data = p.concat(course_data_list,ignore_index=True)    
    
    data = p.concat(data_list,ignore_index=True)
    data.insert(loc=0, column = 'SID_matched', value = 0)   
    
    data_raw = data.copy() #the original imported data set
    if reloading == False:
        data = match_and_clean_large_data(data_raw)



############~~~~~~~ QUERY FUNCTIONS ~~~~~~~###############

def data_query(datain,**kwargs):
    '''Requires all inputs to be submitted as a list
    Example: data_query(data,University = ['Luther_College'], q27a = [3,4,5])'''
    #if no kwargs are given, just return d, this is more likely the case when
    #it is called by data_query_matched
    if not kwargs:
        return datain
    for kw in kwargs:
        #print(kw)
        #print(isinstance(kw,str))
        if isinstance(kwargs[kw],list): #skip the keyword if the option is empty
            #print(kwargs[kw])             
            if len(kwargs[kw]) == 0: #if the keyword is an empty list, return an empty dataframe
                return p.DataFrame([])
            list1 = []
            for l in kwargs[kw]:
                #print(l)
                d1 = datain[datain[kw]==l]
                list1.append(d1)
                #print(list1)
            d1 = p.concat(list1)
            datain = d1
        else :           
            d1 = datain[datain[kw]==kwargs[kw]]
            datain = d1
    return d1    

def course_name_query(**kwargs):
    '''Returns list of course names corresponding to the keyword arguments'''    
    global course_data
    cd2=[]
    cd=data_query(datain=course_data,**kwargs)
    for l in cd['Instructor_html']:                
        if isinstance(l,str):
            cd2.append(l)    
    return cd2

def drop_empty_rows(datain):
    '''
    This function drops all of the data rows that have 0s for all of the questions.
    Used only in initialize_data.
    usage:
    to_drop = drop_empty_rows(data)                             # get the rows to drop
    data = data.drop(to_drop)
    '''
    todrop=[]                                                   #initialize empty list
    column_names = datain.columns
    q_list=[]  #list of all likert scale questions
    for column in column_names:                                 #get a Likert-scale question
        if column[0]=='q':
            q_list.append(column)
    for response in datain.index:
        cum_response = 0
        for question in q_list:                                 #Add all the Likert-scale responses
            r = datain[question][response]
            if isinstance(r,int) or isinstance(r,float):
                cum_response = cum_response + r
        if cum_response ==0:                                    #if cum_response is zero, i.e. the responder didn't answer Likert questions
            todrop.append(response)                             #add it to list of rows you want to drop
    return todrop

def remove_duplicates(d_in,print_output=False) :
    """
    Probably makes most sense for the input dataframe d to be restricted to 
    a particular course.
    Also, probably makes sense for the q40a and q40b test to be run.
    This function will match on first name, last name, and SID and look for near matches as well.
    And keep the valid entry with the earliest date and time stamp.    
    """
    d = d_in.copy()    
    d = data_query(d,q40a=[4], q40b=[4])  
    d_pre = data_query(d,PrePost='Pre')
    d_post = data_query(d,PrePost='Post')  
    
     #for each pre-entry create a matching score between pre and post
    partial_match_1of3 = 0    
    partial_match_2of3 = 0
    SID_match = 0    
    
    drop_duplicates = [] #list of indices to drop
    #match_unique_ID  = match_unique_ID.apply(str)
          
    #loop over all the possible matches and test for 2 of 3 matches
    for prepost in ['Pre','Post'] :
        d_sub = data_query(d,PrePost=prepost)
        
        for ind_sub in d_sub.index :
            sub_row = d_sub.loc[ind_sub,:]
            
            for ind_sub_b in d_sub.drop(ind_sub).index :
                sub_b_row = d_sub.loc[ind_sub_b,:]
                score = 0
                #make sure to clean up the strings before matching
                if clean_str(str(sub_row['First_Name'])) == clean_str(str(sub_b_row['First_Name'])) :
                    score += 1
                if clean_str(str(sub_row['Last_Name'])) == clean_str(str(sub_b_row['Last_Name'])) :
                    score += 2
                if clean_str(str(sub_row['SID'])) == clean_str(str(sub_b_row['SID'])) :
                    score += 2
                    SID_match +=1
                if score >= 1:
                    partial_match_1of3 += 1
                if score >= 3:  #Must match 2 of 3                
                    #unique_ID = str(sub_row['SID'])+'_'+str(sub_b_row['SID'])  
                    #drop row ind_sub if it occurs at a later time
#                    print str(score) + ' ' + str(sub_row['Fname']) + ' ' + str(sub_row['Lname'])
                    if sub_row['StartDate'] > sub_b_row['StartDate'] :
                        drop_duplicates.append(ind_sub)
                    # elif sub_row['Date'] == sub_b_row['Date'] and sub_row['Time'] > sub_b_row['Time'] :
                    #     drop_duplicates.append(ind_sub)
                    # elif sub_row['Date'] == sub_b_row['Date'] and sub_row['Time'] == sub_b_row['Time']:
                    #     if ind_sub > ind_sub_b:
                    #         drop_duplicates.append(ind_sub)
                    else : #don't drop
                        continue
                    partial_match_2of3 += 1                
                    if print_output == True:                
                        print(str(score) + ' | ' + \
                          str(sub_row['First_Name']) + '?' + str(sub_b_row['First_Name']) + ' | ' + \
                          str(sub_row['Last_Name']) + '?' + str(sub_b_row['Last_Name']) + ' | ' + \
                          str(sub_row['SID']) + '?' + str(sub_b_row['SID']))
#    print drop_duplicates
    d = d.drop(drop_duplicates)  
    
#    match_unique_ID_df = p.DataFrame(match_unique_ID, columns=['SID_unique'])
#    d = p.concat([d,match_unique_ID_df], axis=1)  
#    d = d[d['SID_unique'] != '0']  #only return the items which have a match    
    
    return d
             
def make_matched_subset_fuzzy(d_in,print_output=False) :
    """
    Probably makes most sense for the input dataframe d to be restricted to 
    a particular course.
    Also, probably makes sense for the q40a and q40b test to be run.
    This function will match on first name, last name, and SID and look for near matches as well.
        
    """
    d = d_in.copy()    
    d = data_query(d,q40a=[4], q40b=[4])    
    d_pre = data_query(d,PrePost='Pre')
    d_post = data_query(d,PrePost='Post')
    #for each pre-entry create a matching score between pre and post
    partial_match_1of3 = 0    
    partial_match_2of3 = 0
    SID_match = 0    
    
    match_unique_ID = p.Series(np.zeros(len(d),dtype=np.int),name='SID_unique',index=d.index)
    match_unique_ID  = match_unique_ID.apply(str)
          
    #loop over all the possible matches and test for 2 of 3 matches
    for ind_pre in d_pre.index :
        pre_row = d_pre.ix[ind_pre]
        
        for ind_post in d_post.index :
            post_row = d_post.ix[ind_post]
            score = 0
            #make sure to clean up the strings before matching
            if clean_str(str(pre_row['First_Name'])) == clean_str(str(post_row['First_Name'])) :
                score += 1
            if clean_str(str(pre_row['Last_Name'])) == clean_str(str(post_row['Last_Name'])) :
                score += 2
            if clean_str(str(pre_row['SID'])) == clean_str(str(post_row['SID'])) :
                score += 2
                SID_match +=1
            if score >= 1:
                partial_match_1of3 += 1
            if score >= 3:  #Must match 2 of 3                
                unique_ID = str(pre_row['SID'])+'_'+str(post_row['SID'])  
                match_unique_ID[ind_pre] = unique_ID
                match_unique_ID[ind_post] = unique_ID
                partial_match_2of3 += 1                
                if print_output == True:                
                    print(str(score) + ' | ' + \
                      str(pre_row['First_Name']) + '?' + str(post_row['First_Name']) + ' | ' + \
                      str(pre_row['Last_Name']) + '?' + str(post_row['Last_Name']) + ' | ' + \
                      str(pre_row['SID']) + '?' + str(post_row['SID']))
    match_unique_ID_df = p.DataFrame(match_unique_ID, columns=['SID_unique'])
    d = p.concat([d,match_unique_ID_df], axis=1)  
    d = d[d['SID_unique'] != '0']  #only return the items which have a match
    
    #Goal: Remove the duplicate entries that have identical 'SID_unique'
    match_counts = d['SID_unique'].value_counts()
    duplicates = match_counts[(match_counts > 2) + (match_counts == 1)] #A series with SID_uniques that occur more than 2 times
    duplicates_SID_unique_list = duplicates.index.tolist() #the list of SID_uniques
    duplicates_index = data_query(d,SID_unique=duplicates_SID_unique_list).index #the corresponding indices
    d = d.drop(duplicates_index) #drop the duplicate indices
    
    #Remove one 
    
    #print summary
    if print_output == True :    
        print("SID matches     = " + str(SID_match))
        print("partial matches 2 of 3 = " + str(partial_match_2of3))
        print("matches after duplicates removed = " + str(len(d)) + "/2 =" +  str(len(d)/2))
    return d


# I believe this function can be removed for dealing with one class at a time.
def match_and_clean_large_data(data_in):
    '''
    Call this routine to clean data in a large set that contains mulitple classes.
    It loops over all courses, calls 'data' the clean data and 'data_raw' the
    raw imported data.
    ''' 
    print("Removing duplicates and matching...")
    data_temp = None    
    year_list = data_in['Year'].value_counts().index.tolist()
    for year in year_list :
        data_year = data_query(data_in,Year=year)        
        semester_list = data_year['Semester'].value_counts().index.tolist()
        for semester in semester_list :
            data_semester = data_query(data_year,Semester=semester)
            class_list = data_semester['Class'].value_counts().index.tolist()
            if 'nan' in class_list:
                class_list.remove('nan')
            if 'empty' in class_list:
                class_list.remove('empty')
            for class_name in class_list :
                print("{} {} {}".format(year,semester, class_name))                
                data_class = data_query(data_semester,Class=class_name)
                data_class = remove_duplicates(data_class)                
                data_class = make_matched_subset_fuzzy(data_class)
                #append the cleaned and matched class data to the data set..
                if data_temp is None:
                    data_temp = data_class
                else : #append
                    data_temp = p.concat([data_temp,data_class])  
    return data_temp

def match_subset(d):
    """
    Returns a list of the unique IDs.
    """
    #get pre SIDs
    d_pre = data_query(d,PrePost='Pre')
    sidlist_pre = d_pre['SID_unique'].value_counts() # get a list of the SID and count how many time each appears
    sidlist_pre_single = sidlist_pre[sidlist_pre==1]   # only include SIDs that show up once in Pre data
    #get post SIDs
    d_post = data_query(d,PrePost='Post')
    sidlist_post = d_post['SID_unique'].value_counts()
    sidlist_post_single = sidlist_post[sidlist_post==1] # only include SIDs that show up once in post data

    matchlist = sidlist_pre_single + sidlist_post_single
    matchlist = matchlist[matchlist==2]  # only include sids that show up twice in the combined pre/post list
    matchvals = matchlist.index.values
    matchvals_int = []
    for a in matchvals :
        matchvals_int.append(str(a))
    #d_match = data_subset_modified(d,SID=matchvals_int)
    return matchvals_int
    
def get_categories(semyear):
    '''Get the names of the categories.'''
    indices=header_pre[semyear].index
    categories = indices[4::]
    return categories    

def get_class_level(name='calc-intro'):
    """
    Options for class name = 'non-calc-intro', 'calc-intro', 'upper-div'
    
    Can input name='course_name'
    
    returns course level name and a list of courses
    """
    global course_data
    courses = list(data['Class'].value_counts().index)
    if 'empty' in courses: courses.remove('empty')
    if name in courses:
        course_info = course_data[course_data['Instructor_html']==name]
        course_level= course_info['Alg_Calc_Other_Letter'].values[0]
        #name of the course level
        if course_level == 'A':
            course_level_name = 'non-calc intro'
        elif course_level == 'C':
            course_level_name = 'calc intro'
        else:
            course_level_name = 'upper div'
    else:
        course_level_name = name
        if course_level_name == 'all':
            course_list = list(set(data['Class']))
            course_list.remove('empty')
        else:
            type_to_letter = {'non-calc-intro':'A', 'calc-intro':'C', 'upper-div':'O'}
            course_level = type_to_letter[course_level_name]
    course_list = course_name_query(Alg_Calc_Other_Letter=course_level)
    course_list = list(set(course_list)) #To combat duplication of courses that show up in multiple semesters
    return course_level_name,course_list
   
def get_q_list(qtype='personal', category='all'):
    """
    Options are qtype = 'personal', 'professional', 'grade', 'practice'
    
    If category = 'all' then include all questions, otherwise pick out the
    subset that have the desired category.
    """
    type_to_letter = {'personal':'a', 'professional':'b', 'grade':'c', 'practice':'d'}
    #print type_to_letter[qtype]
    q_list = []    
    for cols in data:
        #print cols
        if cols[0]=='q' and cols[3]==type_to_letter[qtype]:
            if cols[1]!='4':                            #don't want q40a
                q_list.append(cols)               
    # Now pick out the subset of questions that have the assigned category...
    #return the whole list for 'grade' or 'practice' because we don't have 
    # post header metadata right now.
    if qtype == 'grade' or qtype == 'practice' :
        return q_list
    elif category == 'all' :
        return q_list
    #Otherwise loop over the questions and see if they are in the right category       
    else :
        #print "Made it to the else statment!"        
        q_in_cat_list=[]
        for question in q_list:
            if header_pre[question][category]=='y':
                q_in_cat_list.append(question)
        return q_in_cat_list
    
def _get_new_table_dir(s=''):
    """
    Makes a new directory in the tables directory with current date.
    Adds optional string s to the end of the directory name.
    The "Tables" directory must already exist, because you can't add a 
    subdirectory to a non-existent directory.
    """
    today = dt.datetime.now()
    dirname = today.strftime("%Y-%m-%d %I.%M.%S %p")
    if _user == 'Ben' :
        full_dir = _table_directory + dirname + " " + s + '\\'  #Ben
    elif _user == 'Takako' :
        full_dir = _table_directory + dirname + " " + s + '/'   #Takako
    print(full_dir)
    if os.path.isdir(full_dir) == False:
        os.mkdir(full_dir)
    return full_dir

def _get_new_graph_dir(s=''):
    """
    Makes a new directory in the graphs directory with current date.
    Adds optional string s to the end of the directory name.
    The "Graphs" directory must already exist, because you can't add a 
    subdirectory to a non-existent directory.
    """
    today = dt.datetime.now()
    dirname = today.strftime("%Y-%m-%d %I.%M.%S %p")
    if _user == 'Ben':
        full_dir = _graph_directory + dirname + " " + s + '\\' #Ben
    elif _user == 'Takako':
        full_dir = _graph_directory + dirname + " " + s + '/'   #Takako
    print(full_dir)
    if os.path.isdir(full_dir) == False:
        os.mkdir(full_dir)
    return full_dir

############~~~~~~~~~~ HELPER FUNCTIONS ~~~~~~~~~~~##################
                
def wrap_text(text,line_len=60):    
    words = text.split(' ')
    linelist = [''] #start off with a one line empty list
    counter = 0    
    for word in words :
        if len(linelist[counter]) + 1 + len(word) <= line_len :
            if len(linelist[counter]) > 0  :
                linelist[counter] += ' '  #Add a space before appending the word unless the line is empty
            linelist[counter] += word  #Append the word
        else :
            linelist.append(word) #create a new line and add the new word
            counter += 1
    
    return '\n'.join(linelist) #join all the lines together with no separator  

def clean_str(string) :
    """
    strips leading white spaces from string and makes lowercase.
    
    Used in the matching function.
    """    
    string = string.strip() #strip off leading and trailing white spaces
    string = string.lower() #make the whole string lowercase
    return string
    
def change_q_type(q,q_type2):
    '''generalize the q.replace('a','b') routines to include all q_types.'''
    #identify type of question q is
    q_type1 = det_q_type(q)
    type_to_letter = {'personal':'a', 'professional':'b', 'grade':'c', 'practice':'d'}
    q2 = q.replace(type_to_letter[q_type1],type_to_letter[q_type2])
    q_list = get_q_list(qtype=q_type2)
    inlist = False
    if q2 in q_list:
        inlist = True
    #return q2, inlist
    return q2
    
def det_q_type(q):
    '''input the question name (i.e. 'q10a') and get the question type in return.'''
    letter_to_type = {'a':'personal', 'b':'professional', 'c':'grade', 'd':'practice'}
    qtype = letter_to_type[q[3]]
    return qtype
        
def Hist2D_corr_drop(datain):
    '''Used by Hist2D_process_data to ID rows that have responses out of range
    and tell Hist2D_process_data to drop them.'''
    todrop = []
    for stud in datain.index:
        if datain.ix[stud,1]==0 or datain.ix[stud,2]==0:
            todrop.append(stud)
        elif datain.ix[stud,1]==6 or datain.ix[stud,2]==6:
            todrop.append(stud)
    return todrop

def tick_labels(q_type):
    '''return a list of tick labels for plots depending on question type'''
    if q_type == 'personal' or q_type == 'professional':
        labels = ('strongly\ndisagree','disagree','neutral','agree','strongly\nagree')
    if q_type == 'grade':
        labels = ('very\nunimportant',' ','neutral',' ','very\nimportant')
    if q_type == 'practice':
        labels = ('very\nrarely',' ','neutral',' ','very\nfrequently')
    if q_type == 'expertlike':
        labels = ('highly\nnon-expert-like','non-expert-\nlike','neutral','expert-\nlike','highly\nexpert-like')
    if q_type == 'expertlike,short':
        labels = ('highly\nnon-expert-like',' ','neutral',' ','highly\nexpert-like')
    return labels
    
def round_corr(corr):
    '''round the Pearson R correlation outputs'''
    corr_val = round(corr[0],3)
    p_val = round(corr[1],3)
    rounded = (corr_val,p_val)
    return rounded
       
################~~~~~~~~~~ ANALYSIS FUNCTIONS ~~~~~~~~~~################

def interleaved_hist(datain,datain_name,semyear,savefigs=False):
    '''Interleaved histogram. 
    datain      = a list of Series. Each Series is used as a bar
    datain_name = a list of names for each Series. Must be the same length as datain
    count_these = a list of numbers that correspond with the Series you want counted
                  to get the total number of respondents
    savefigs= True/False; whether you want to save the figure.
    '''
    colorcycle = ['r','m','orange','y','c']
    num_bars=len(datain)
    width=round(1.0/(num_bars+.5),2)
    if savefigs == True:
        dir = _get_new_graph_dir("Grade_Practice_histograms")    
    ind=np.arange(5)
    fig=py.figure(figsize=fig_size)
    ax=fig.add_subplot(111)
    histograms = []
    q = datain[0].name
    name = '_'
    total_num = 0
    for data in range(len(datain)):
        d = datain[data]
        if q=='q30c':
            d = d.apply(np.float)      
        d_hist, d_err = hist_process_data(d,semyear) 
        
        hist_d= hist_with_err(ax,d_hist, d_err,width,data,ind,colorcycle[data])
        histograms.append(hist_d[0])
        name = name+datain_name[data]+'_'
    
    if len(datain)==2:
        corr = pearsonr(datain[0],datain[1])    
        rounded_corr = round_corr(corr)     
        title = header_post[semyear][q][0]+' N='+str(total_num)+' r='+str(rounded_corr)
    else:
        title = header_post[semyear][q][0]+' N='+str(total_num)
    py.suptitle(wrap_text(title),fontsize=font_size) 
    ax.legend(histograms,datain_name,loc=0,fontsize=font_size)
    py.xlabel('Response',fontsize=font_size)
    py.ylabel('Number of Respondents',fontsize=font_size)
    ax.set_xticks(ind+(num_bars/2.0)*width)
    ax.set_xticklabels(tick_labels('expertlike,short'),fontsize=font_size)            
    py.tight_layout()
    py.subplots_adjust(top = 0.85)
    if savefigs == True :         
        filename=q+name+"interleaved_histograms" + ".PNG"
        py.savefig(dir+filename,dpi=dots_per_inch)
        py.close()
    return

def survey_score_distribution_hist(datain, datain_names, savefigs=False):
    ''' Plots interleaved histograms showing the distribution of percent expert-like responses.
    
    datain      = a list of data subsets. These subsets assume a class or class 
                  level, Pre or Post, matched responses and specific questions 
                  have already been picked out using data_query and .loc 
                  functions. Be sure to include Class and PrePost.
                  If only one entry is given, remember to put it in []
    datain_names= a list of names for each of these data subsets. This must
                  match the length of datain
                  If only one entry is given, remember to put it in []
    savefigs    = True/False
    '''
    sfactor=1. #vertical scale factor
    colorcycle = ['b','g','r','c','m','y','k','orange']
    colors = colorcycle[0:len(datain)]
    expertlike = []
    total_num = 0
    for dataset in datain:
        expertperc = score_dist_process_data(dataset,sfactor)
        expertlike.append(expertperc)
        total_num = total_num + len(dataset)
    
    num_datain = len(datain)
    
    #Determine the kind of data set was inputted
    if num_datain==1:
        classes = list(set(datain[0]['Class']))
        all_classes = data_query(data,PrePost = 'Pre')
        all_class_num = list(set(all_classes['Class']))
        if len(classes)==all_class_num: 
            course_name = 'all'
        elif len(classes)>1 and len(classes)<len(set(data['Class'])):
            course_name,course_list = get_class_level(classes[0])
        else:
            course_name = classes[0]
    
    #Make figure
    fig = py.figure(figsize=fig_size)
    ymaxs = []
    
    for x in range(num_datain):
        ax = fig.add_subplot(num_datain,1,x)
        py.hist(expertlike[x],bins=10, range=(0,sfactor*1), normed=True,color=colors[x], label=datain_names[x])
        py.xlim((0,1*sfactor))
        py.ylim(ymin=0)
        ymaxs.append(ax.get_ylim()[1])
        py.title(datain_names[x],fontsize=font_size)
        py.xlabel('% Expertlike Response')
        py.ylabel('Number of Respondents',fontsize=font_size)
        ax.set_xticks(sfactor*np.array([.25,.45,.65,.85]))
        ax.set_xticklabels(['20%','40%','60%', '80%'],fontsize=font_size)
    
    y_max = max(ymaxs)
    for x in range(num_datain):
        ax = fig.add_subplot(num_datain,1,x)
        py.ylim(ymax=y_max)
    
    title_text = wrap_text('Response Expertlike Distribution \n N='+str(total_num))
    py.suptitle(title_text)
    py.tight_layout()
    py.subplots_adjust(top=0.9)
    
    if savefigs == True :  
        dir = _get_new_graph_dir("Distribution_histograms")  
        if len(datain)==1:
            filename=course_name+"_distribution_histograms" + ".PNG"
        else:
            filename = "Distribution_histograms" + ".PNG"
        py.savefig(dir+filename,dpi=dots_per_inch)
        py.close()
    return    

def pre_post_2D_hist(preresponses, postresponses,savefigs=False): 
    ''' Makes a 2D histogram. The x-axis is the pre-semester reponse, while the y-axis 
    is the post-semester response. Since it uses matched respondents, the shift is 
    implicit in the position on the graph. Expertlike shift is denoted by a position 
    above the y=x boxes, whilea non-expertlike shift is denoted by a position below
    the y=x boxes.
    
    NOTE: preresponses and postresposes should be inputted using loc function. ASSUMES
    DATA HAS BEEN MATCHED! preresponses and postresponses are going to have a different
    number of data columns since preresponses requires 'Semester', and 'Year' columns
    i.e. 
    pre1 = basic.data_query(basic.data,PrePost='Pre')
    post1 = basic.data_query(basic.data,PrePost='Post')
    basic.pre_post_2D_hist(pre1.loc[:,['SID_unique','Semester','Year','q01a']],post1.loc[:,['SID_unique','q01a']])
    '''
    #sem = list(set(preresponses.loc[:,'Semester']))[0]
    #year = list(set(preresponses.loc[:,'Year']))[0]
    #sem_year = sem[0:2]+year[2:4]  #take the first two letters of semester and last 2 number of year
    if savefigs == True:
        dir = _get_new_graph_dir("Pre_Post_Shift")
    q = preresponses.ix[:,1].name                  # determine the question # from the array.
    fig = py.figure(figsize=fig_size)
    CS_per = fig.add_subplot(1,1,1)
    num_matched = len(preresponses['SID_unique'])
    datarray, percentage = Hist2D_process_data(preresponses,postresponses)
    #plot_2d_hist(datarray,CS_per)
    CS_per = plot_2d_hist(datarray,CS_per)
    CS_per.set_xticks((1.,2.,3.,4.,5.))
    CS_per.set_xticklabels(tick_labels('expertlike,short'),fontsize=font_size)
    CS_per.set_yticks((1.,2.,3.,4.,5.))
    y_ticklabels = ['highly\nnon-expertlike\n\n ',' ','neutral\n',' ','highly\nexpertlike\n\n ']
    CS_per.set_yticklabels(y_ticklabels,fontsize=font_size,rotation='vertical',ha='center',va='center')
    #Question text as title
    title= header_pre[q][0]+' N='+str(num_matched)
    py.suptitle(wrap_text(title),fontsize=font_size)
    CS_per.set_xlabel('Pre-response',fontsize=font_size)
    CS_per.set_ylabel('Post-response',fontsize=font_size)
    CS_per.set_title('Personal',fontsize=font_size)
    
    #py.tight_layout()
    py.subplots_adjust(top = 0.9) 
    #py.show()
    if savefigs == True :         
        filename = + q + "_" + "Pre_Post_Shift_Personal" + ".PNG"
        py.savefig(dir+filename,dpi=dots_per_inch)
        py.close()

    return fig, CS_per

def q1_q2_2D_hist(datain1,datain2,savefigs=False): #course
    ''' Makes a 2D histogram using two different questions. Each axis represents 
    the response distribution of each question. The x-axis corresponds with datain1, 
    while the y-axis corresponds to datain2. The data is sent to a data processing 
    function (Hist2D_question_process_data) and then to the 2D histogram plotting 
    function (plot_2d_hist). Additionally uses the det_q_type function to determine 
    the question type the inputted columns are. The biggest difference between 
    this function and the preceding pre_post_2D_hist function is the way the labels 
    are done.
    
    NOTE: datain1 and datain2 should be inputted using loc function.
    basic.pre_post_2D_hist(some_data.loc[:,['SID_unique','Semester','Year','q01a']],some_data.loc[:,['SID_unique','Semester','Year','q01b']])
    '''
    sem1 = list(set(datain1.loc[:,'Semester']))[0]  
    year1 = list(set(datain1.loc[:,'Year']))[0]
    sem_year = sem1[0:2]+year1[2:4]
    
    sem2 = list(set(datain2.loc[:,'Semester']))[0]  
    year2 = list(set(datain2.loc[:,'Year']))[0]
    if sem1!=sem2 or year1!=year2:
        print('NOTE: datain1 and datain2 are from different semesters!')
    
    q = datain1.ix[:,3].name
    p = datain2.ix[:,3].name
    qtype1 = det_q_type(q)
    qtype2 = det_q_type(p)
    if savefigs == True:
        dir = _get_new_graph_dir(qtype1+"_vs_"+qtype2+"_plots")
    num_matched = len(datain1['SID_unique'])                     #this is here to get the corresponding expert response.
    
    py.figure(figsize=fig_size)
    CS=py.subplot(111)
    #make the 2D hist, calculate the percentage on the diag, correlation
    datarray,percentage,corr=Hist2D_process_data(datain1.loc[:,['SID_unique',q]],datain2.loc[:,['SID_unique',p]],sem_year,include_corr=True)
    plot_2d_hist(datarray,CS)
    percentage = round(float(percentage),2)
    #title is number of matched responses, correlation between questions and percentage on diagonal
    title= ' N='+str(num_matched)+' corr='+str(corr)+'\n Percentage on diagonal:'+str(percentage)
    py.suptitle(wrap_text(title),fontsize=14)
    CS.set_xlabel(wrap_text(header_post[sem_year][q][0]),fontsize=font_size)
    CS.set_ylabel(wrap_text(header_post[sem_year][p][0]),ha='center',va='center',fontsize=font_size)                
    CS.set_xticks((1.,2.,3.,4.,5.))
    CS.set_xticklabels(tick_labels(qtype1),fontsize=font_size)
    CS.set_yticks((1.,2.,3.,4.,5.))
    ticklabels = tick_labels(qtype2)
    y_ticklabels = [s+'\n' for s in ticklabels]
    CS.set_yticklabels(y_ticklabels,fontsize=font_size,rotation='vertical',ha='center',va='center')
    py.tight_layout()
    py.subplots_adjust(top=0.9)
    py.show()
    if savefigs == True :         
        filename=q+"_"+qtype1+"_vs_"+qtype2+ ".PNG"
        py.savefig(dir+filename,dpi=dots_per_inch)
        py.close()
        
    return CS

def shift_vs_q_scatterplot(datain,savefigs=False):
    '''creates a scatterplot with the shift on the y-axis and the grade on the x-axis
    
    course_list = list of courses. The courses will be grouped together.
    category    = the category plotted in the scatterplot/'all'
    savefigs    = True/False; whether you want to save the figure(s) generated.'''
    
    sem = list(set(datain['Semester']))[0]
    year = list(set(datain['Year']))[0]
    sem_year= sem[0:2]+year[2:4]
    
    grade_qs=get_q_list(sem_year,qtype='personal')
    pre_responses = data_query(datain, PrePost = 'Pre')
    post_responses=data_query(datain, PrePost = 'Post')
    num_matched = len(pre_responses)
    py.figure(figsize=fig_size)
    ax=py.subplot(111)
#    ax.plot([0,5],[0,0],'k--',alpha=0.2)
    pq_shift_ave_list = []
    gq_ave_list = []
    for gq in grade_qs:
        pq,inlist = change_q_type(gq,'personal')
        if inlist==True:
            shift_sum=0
            grade_q_sum=0
            for studid in pre_responses['SID_unique']:
                pre_response = data_query(pre_responses,SID_unique=studid)[pq]
                post_response = data_query(post_responses,SID_unique=studid)[pq]
                pre = float(pre_response.values[0])
                post = float(post_response.values[0])
                shift_sum = shift_sum + (post-pre)
                if header_post[sem_year][pq][3] == 'n':
                    shift_sum=-shift_sum
                grade_response = data_query(post_responses,SID_unique=studid)[gq]
                grade_q_response = float(grade_response.values[0])
                if header_post[sem_year][gq][3] == 'n':
                    grade_q_response = -(grade_q_response-3)+3
                grade_q_sum = grade_q_sum+grade_q_response
            pq_shift_ave = shift_sum/num_matched
            gq_ave=grade_q_sum/num_matched
            pq_shift_ave_list.append(pq_shift_ave)
            gq_ave_list.append(gq_ave)
            ax.plot(gq_ave,pq_shift_ave,'o')
            py.annotate(gq,xy=(gq_ave+0.02,pq_shift_ave),verticalalignment='center')
        else:
            print((gq+" does not have a 'personal' equivalent"))
    corr = pearsonr(pq_shift_ave_list,gq_ave_list)
    rounded_corr = round_corr(corr)
    
    py.xlabel('personal',fontsize=font_size)
    py.ylabel('Pre/Post Shift',fontsize=font_size)
    py.suptitle('Shift vs personal N='+str(int(num_matched))+'\nCorrelation='+str(rounded_corr),fontsize=font_size)
    
    if savefigs == True:
        dir = _get_new_graph_dir("shift_vs_personal_scatterplots")
        filename = "Shift_vs_personal_Scatterplot"+".PNG" 
        py.savefig(dir+filename,dpi=dots_per_inch)
        py.close()
    
    return

def q1_vs_q2_scatterplot(datain,qtype1='grade',qtype2='personal',savefigs=False):
    '''Question type vs diff question type scatterplot. Includes correlation between 
    two matching questions.
    
    course_list = list of courses
    qtype1      = qtype on x-axis
    qtype2      = qtype on y-axis
    category    = category name/'all'
    savefigs    = True/False; whether you want to save the figures generated.
    '''
    sem = list(set(datain['Semester']))[0]
    year = list(set(datain['Year']))[0]
    sem_year= sem[0:2]+year[2:4]
    
    grade_qs=get_q_list(sem_year,qtype=qtype1)
    pre_responses= data_query(datain,PrePost = 'Pre')
    post_responses = data_query(datain,PrePost= 'Post')
    num_matched = len(pre_responses)
    py.figure(figsize=fig_size)
    ax=py.subplot(111)
    ax.plot([0.5,5.5],[0.5,5.5],'k--',alpha=0.2)
    pq_post_ave_list = []
    gq_ave_list = []
    for gq in grade_qs:
        pq,inlist = change_q_type(gq,qtype2)
        if inlist == True:
            post_sum=0
            grade_q_sum=0
            for studid in pre_responses['SID_unique']:
                post_response = data_query(post_responses,SID_unique=studid)[pq]
                post = float(post_response.values[0])
                if header_post[sem_year][pq][3] == 'n':
                    post = -(post-3)+3
                post_sum=post_sum+post
                grade_response = data_query(post_responses,SID_unique=studid)[gq]
                grade_q_response = float(grade_response.values[0])
                if header_post[sem_year][gq][3] == 'n':
                    grade_q_response = -(grade_q_response-3)+3
                grade_q_sum = grade_q_sum+grade_q_response
    #            print post_response,grade_q_response
            pq_post_ave = post_sum/num_matched
            gq_ave=grade_q_sum/num_matched
            pq_post_ave_list.append(pq_post_ave)
            gq_ave_list.append(gq_ave)
            ax.plot(gq_ave,pq_post_ave,'o')
            py.annotate(gq,xy=(gq_ave+0.02,pq_post_ave),verticalalignment='center')
        else:
            print((gq+' does not have a '+qtype2+' equivalent'))
    ax.set_xlim(.5,5.5)  
    ax.set_ylim(.5,5.5)     
    corr = pearsonr(pq_post_ave_list,gq_ave_list)
    rounded_corr = round_corr(corr)
    
    ax.set_xticks((1,2,3,4,5))
    ax.set_xticklabels(tick_labels(qtype1),fontsize=font_size)
    ax.set_yticks((1,2,3,4,5))
    ticklabels = tick_labels(qtype2)
    y_ticklabels = [s+'\n' for s in ticklabels]
    ax.set_yticklabels(y_ticklabels,fontsize=font_size,rotation='vertical',ha='center',va='center')
    py.xlabel(qtype1,fontsize=font_size)
    py.ylabel('Post'+qtype2,fontsize=font_size)
    py.suptitle(qtype2+' vs '+qtype1+' N='+str(int(num_matched))+'\nCorrelation='+str(rounded_corr),fontsize=font_size)
    py.tight_layout()
    py.subplots_adjust(top=0.9)
    if savefigs == True:
        dir = _get_new_graph_dir(qtype2+"_vs_"+qtype1+"_scatterplots")
        filename = qtype2+"_vs_"+qtype1+"_Scatterplot"+".PNG" 
        py.savefig(dir+filename,dpi=dots_per_inch)
        py.close()
    
    return    

def gains_1D_compare2(datain1,datain2,datain1_name,datain2_name,savefigs=False,\
            sortby='pre',qtype='personal', exp_nonexp='expertlike'):
    """
    This function assumes the user selects the subset of courses prior to calling
    the gains_1D_categories function
    
    "savefigs" will save a high res PNG and a PDF of the figure when set to True.
    
    "sortby" can take on values 'pre', 'post', or 'shift'.  THe sorting
    starts with most positive at the top, and least positive at the bottom.
    
    "qtype" should be 'personal', 'professional', 'grade', 'practice'
    
    "exp_nonexp" lets user choose whether expertlike ('expertlike') or non-expertlike ('nonexpertlike' fractions 
    are plotted. 
    It is really a matter of whether the data is projected on the expertlike or 
    non-expertlike axis.
    
    """
    if savefigs == True:
        dir = _get_new_graph_dir("gains_1D")    
       
    fig_size = (14,8)
    gridspec_width_ratio = [1,2] 
    fig = py.figure(figsize=fig_size)
    gs = gridspec.GridSpec(1, 2,width_ratios=gridspec_width_ratio)
    ax = fig.add_subplot(gs[0])
    #ax = fig.add_subplot(121)    
    ax.set_xlim(0,1)  
    
    #Add vertical grid lines    
    ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')    
#    offset = 0.2    
    
    data1 = gains_1D_process_data(datain1,qtype=qtype)
    data2 = gains_1D_process_data(datain2,qtype=qtype) 
    
    #do the sorting (assuming 'pre')
    df = data1.copy()
    num_match_series= df['pre_expert']+df['pre_nonexpert']+df['pre_neutral']    
    sortby_series = 1.0*df['pre_expert']/num_match_series
    
    plot_gains_1D(ax,data1, sortby_series, offset=.2,colour='r', exp_nonexp='expertlike', \
                sortby=sortby_series, qtype='personal', categories=False, \
                plot_title=False, text_labels=True,first = True)
    plot_gains_1D(ax,data2, sortby_series, offset=-.2,colour='b', exp_nonexp='expertlike', \
                sortby=sortby_series, qtype='personal', categories=False, \
                plot_title=False, text_labels=False,first = False)    
#    ax.legend([circ1,circ2],[datain1_name,datain2_name],bbox_to_anchor=(.01,1),loc=2)
    py.suptitle('What do you think?')
    if savefigs == True :         
        filename = datain1_name+"_vs_"+ datain2_name +"_gains_1D" + ".PNG"
        py.savefig(dir+filename,dpi=dots_per_inch)
        filename = datain1_name+"_vs_"+ datain2_name +"_gains_1D" + ".PDF"
        py.savefig(dir+filename)
        
    #categories
    fig_size = (8,8)
    gridspec_width_ratio = [2,1]
     
    fig = py.figure(figsize=fig_size)
    gs = gridspec.GridSpec(1, 2,width_ratios=gridspec_width_ratio)

    ax = fig.add_subplot(gs[0])
    #ax = fig.add_subplot(121)    
    ax.set_xlim(0,1)  
    
    #Add vertical grid lines    
    ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')
    
    data1_cat = gains_1D_process_data(datain1,qtype=qtype,for_categories=True)
    data2_cat= gains_1D_process_data(datain2,qtype=qtype,for_categories=True)
    
    #sort...still needs to be figured out
    df_cat = data1_cat
    num_match_series_cat = df_cat['pre_expert_cat']+df_cat['pre_nonexpert_cat']+df_cat['pre_neutral_cat']
    sortby_series_cat = 1.0*df_cat['pre_expert_cat']/num_match_series_cat

    plot_gains_1D(ax,data1_cat, datain1_name, offset=.2,colour='r',exp_nonexp='expertlike',\
                sortby=sortby_series_cat, qtype='personal', categories=True, \
                plot_title=False, text_labels=True,first=True)
    plot_gains_1D(ax,data2_cat, datain2_name, offset=-.2,colour='b',exp_nonexp='expertlike',\
                sortby=sortby_series_cat, qtype='personal', categories=True, \
                plot_title=False, text_labels=True,first=False)
    plot1_cat_name = datain1_name+' categories'
    plot2_cat_name = datain2_name+' categories'
#    ax.legend([circ1,circ2],[plot1_cat_name,plot2_cat_name],loc=1)
    
    if savefigs == True :         
        filename = datain1_name+"_vs_"+ datain2_name +"_categories_gains_1D" + ".PNG"
        py.savefig(dir+filename,dpi=dots_per_inch)
        filename = datain1_name+"_vs_"+ datain2_name +"_categories_gains_1D" + ".PDF"
        py.savefig(dir+filename)    

################~~~~~~~~~~~ DATA PROCESSING FUNCTIONS ~~~~~~~~~~~~##################

def hist_process_data(datain,scaled=False):
    '''takes in the data and puts it in a form that can be plotted by the numpy
    bar function. '''
    total_num=float(len(datain))
    hist_data, bins_data = np.histogram(datain,bins=5,range=(.5,5.5))
    hist_data.astype(np.float)
    q = datain.name
    #flip the histogram if the question is stated negatively
    if header_post[q][3] =='n':
        hist_data=hist_data[::-1]
    data_err = [0,0,0,0,0]
    for x in range(len(data_err)):
        data_err[x]=hist_data[x]*(1-hist_data[x]/total_num)
    data_err = np.sqrt(data_err)
    if scaled == True:
        hist_data=hist_data/total_num
        data_err = data_err/total_num   
    return hist_data, data_err

def score_dist_process_data(datain,vscale_factor):
    '''Takes in the data in a form that can be plotted by the pyplot hist function. 
    Specifically, it calculates the percent expert-like responses of individual 
    students and returns a list of all of these percentages.'''
    scale=vscale_factor
    columns = datain.columns
    q_list = []
    explike_perc = []
    sem = list(set(datain['Semester']))[0]
    year = list(set(datain['Year']))[0]
    sem_year=sem[0:2]+year[2:4]
    
    #build a list of questions that can actually be used.
    for col in columns:
        if col[0] == 'q':
            q_list.append(col)
            
    #Change the answers for negatively worded-questions to align with positively-
    #worded questions
    for q in q_list:
        if q=='q30c' or q=='q30d':
            datain.ix[:,q] = datain.loc[:,q].apply(np.float)  
        if header_post[sem_year][q][3] == 'n':
            datain.ix[:,q] = -(datain.loc[:,q]-3)+3 
    total_qs = len(q_list)
    
    #To avoid the horror of dividing by zero
    if total_qs ==0: 
        print('No question data were inputted')
        return
    
    for stud in datain.index:
        exp_total = 0
        stud_response = datain.loc[stud,q_list]
        
        values = stud_response.value_counts()
        # Unfortunately, must use for loop to count the expertlike responses
        # since there are cases when a 
        for ind in values.index:
            if ind == 5 or ind == 4: exp_total = exp_total + values[ind]
        explike = scale*float(exp_total)/float(total_qs) + 1e-10
        explike_perc.append(explike)
    
#    hist_data, bins_data = np.histogram(explike_perc,bins=10,range=(-.01,1.1))
    return explike_perc

def Hist2D_process_data(datainx, datainy, include_corr = False):
    '''make a 2D histogram comparing two different questions. It also calculates
    the percentage of responses on the diagonal and the correlation between questions.
    datainx     = data set being used
    datainy     = list of matched responses
    include_corr= Boolean, whether to include correlation
    '''
    datarray = np.zeros((5,5))  
    question = datainx.iloc[:,1].name
    print("question = {}".format(question))
    datain=p.merge(datainx,datainy,how='inner',on='SID_unique')
    print("columns = " + str(datain.columns))
#    xcol_name = datain.iloc[:,1].name  #this code relies on an arbitrary column ordering, that may not be repeatable
#    ycol_name = datain.iloc[:,2].name
    xcol_name = question + "_x"
    ycol_name = question + "_y"
    print("xcol_name = {}, ycol_name = {}".format(xcol_name,ycol_name))
    datain[xcol_name]=datain[xcol_name].apply(np.int64)
    datain[ycol_name]=datain[ycol_name].apply(np.int64)
    num_matched = len(datain['SID_unique'])
    if header_post[question]['Positive-Negative'] == 'n':
        datain.ix[:,[1,2]] = -(datain.iloc[:,[1,2]]-3)+3
    for stud in datain.index:
        if header_post[question]['Positive-Negative'] == 'n':
            if datain.ix[stud,2]==6 :
                num_matched = num_matched-1
            elif datain.ix[stud,1]==6 and datain.ix[stud,2]!=6: #second condition is probably redundant
                num_matched = num_matched-1
            else:
                datarray[datain.ix[stud,2]-1, datain.ix[stud,1]-1]=datarray[datain.ix[stud,2]-1,datain.ix[stud,1]-1]+1
        else: 
            if datain.ix[stud,2]==0:
                num_matched = num_matched-1
            elif datain.ix[stud,1]==0 and datain.ix[stud,2]!=0:
                num_matched = num_matched-1
            else:
                datarray[datain.ix[stud,2]-1, datain.ix[stud,1]-1]=datarray[datain.ix[stud,2]-1,datain.ix[stud,1]-1]+1
    corr = pearsonr(datain[xcol_name],datain[ycol_name])
    rounded_corr=round_corr(corr)
    percentage = str(sum(np.diag(datarray))/num_matched)
    if include_corr == True:
        datain.drop(Hist2D_corr_drop(datain))
        corr = pearsonr(datain[xcol_name],datain[ycol_name])
        return datarray, percentage, rounded_corr
    else:
        return datarray, percentage

def uncertainty_1D_fast(fav_act,unfav_act, num_matched):
    """
    Just compute the uncertainty in the expertlike and non-expertlike dimensions.
    No diagonalizing and returning special parameters like 
    uncertainty_ellipse_params_fast()
    """    
    mean = np.array([fav_act, unfav_act])
    fav, unfav = np.mgrid[0:num_matched+1, 0:num_matched+1]    
    prob_array = prob_dist_fast(fav,unfav, fav_act, unfav_act, num_matched)
    
#    print "Sum of prob_array elements = " + str(prob_array.sum())    
    #Calculate the covariance matrix
    covariance = np.zeros((2,2))  #A 2x2 covariance matrix
    #print ((fav-mean[0])**2 * prob_array).sum()
    covariance[0][0] = np.sum( (fav-mean[0])**2 * prob_array )
    covariance[1][0] = np.sum( (fav-mean[0])*(unfav-mean[1]) * prob_array )
    covariance[0][1] = covariance[1][0]
    covariance[1][1] = np.sum( (unfav-mean[1])**2 * prob_array )
        
    #print "mean = " + str(mean)
    #print "exp_variance = " + str(covariance[0][0]) + "; nonexp_variance = " + str(covariance[1][1])
    fav_uncertainty = np.sqrt(covariance[0][0]) #return uncertainty as std dev.
    unfav_uncertainty = np.sqrt(covariance[1][1])
    return (fav_uncertainty, unfav_uncertainty)

def prob_dist_fast(fav,unfav, fav_act, unfav_act, num_matched):
    """
    Given a population defined by:
    fav_act  = actual number of favorable students
    unfav_act = actual number of unfavorable students
    num_matched = actual total number of students    
    
    Calculate the probability of getting a distribution with:
    fav = number of favorable students
    unfav = number of unfavorable students (total students assumed to be the same)
    
    Accepts matrices for fav and unfav.
    """
    neut_act = num_matched - fav_act - unfav_act
    neut = num_matched - fav - unfav    
    #print neut    
    neut_neg = neut > -0.5 #returns a boolean array where 0,1,2, are true, all negative integers are false
    neut = neut_neg*neut  #converts all negative values to zero, so factorial doesn't return infinity
    #print neut
   #create the normalized probabilities
    p_fav = 1.0*fav_act/num_matched
    p_unfav = 1.0*unfav_act/num_matched
    p_neut = 1.0*neut_act/num_matched
    
           
    #Calculate the probability 
    #prob = p_fav**fav * p_neut**neut *  p_unfav**unfav *\
    #    factorial(num_matched)/(factorial(fav)*factorial(unfav)*factorial(neut))   
    #This way works up to atleast a number of matched above 1000, but breaks at 2000 
    #because the comb function hits the maximum value of a float.
#    prob = p_fav**fav * p_neut**neut *  p_unfav**unfav *\
#        comb(num_matched,fav)*comb(num_matched - fav, unfav)  #The comb function is the N choose k function
    #gammaln(n+1) = log(factorial(n)) but it is computed way more efficiently

    #In the case where p_fav and fav are both zero, the prob should be one, 
    #so log prob should be zero and we need to replace the nan's that result from
    #taking 0*log(0) with zero.

    logprob_fav = fav*np.log(p_fav) 
    logprob_fav = np.nan_to_num(logprob_fav) #+ ones * np.isnan(logprob_fav)
        
    
    logprob_neut = neut*np.log(p_neut) 
    logprob_neut = np.nan_to_num(logprob_neut) #+ ones * np.isnan(logprob_neut)    
    
    logprob_unfav = unfav*np.log(p_unfav) 
    logprob_unfav = np.nan_to_num(logprob_unfav) #ones * np.isnan(logprob_unfav)
    
    factorial_terms =  gammaln(num_matched+1) - gammaln(fav+1) - gammaln(neut+1) - gammaln(unfav+1)
    
    logprob = logprob_fav + logprob_neut + logprob_unfav + factorial_terms
        
    prob2 = np.exp(logprob)
    
#    prob = neut_neg*prob #make all values zero for negative neutral elements
    prob2 = neut_neg*prob2
    
    #print prob2
    return prob2

def gains_1D_process_data(data_in,qtype='personal',for_categories=False) :
    '''
    Given an input data set, returns a dataframe with columns:
    pre_expert_series
    shift_expert_series 
    pre_nonexpert_series 
    shift_nonexpert_series
    pre_neutral_series 
    '''
    sem = list(set(data_in['Semester']))[0]
    year = list(set(data_in['Year']))[0]
    sem_year=sem[0:2]+year[2:4]
    
    #select out a matched subset of valid responses        
    preresponses = data_query(data_in,PrePost= 'Pre')
    postresponses = data_query(data_in, PrePost = 'Post')
    num_matched = len(preresponses)
    if num_matched==0: print("no matched responses");return
    
    q_list = get_q_list(sem_year,qtype)
    
    #Build a series of pre scores and shifts
    pre_expert_dict = {}  #dictionaries indexed by the question number
    pre_nonexpert_dict = {} #need this to compute uncertainty intervals
    pre_neutral_dict = {} #need this to compute uncertainty intervals
    shift_expert_dict = {}
    shift_nonexpert_dict = {} #Need this only to give flexibility in sorting.
    for q in q_list:
        #The code is so fast now, that a status update is not necessary.
        #if q in ['q10a', 'q20a', 'q30a']:        
            #print q  #give a status update
        pre_dist = preresponses[q].value_counts()  #value_counts gives the number of each response
        post_dist = postresponses[q].value_counts()
        #print pre_dist

        #Clean up the pre_dist and post_dist        
        for i in range(1,6):
            if not (i in pre_dist.index) :
                pre_dist = pre_dist.append(p.Series({i:0}))    
            if not (i in post_dist.index) :
                post_dist = post_dist.append(p.Series({i:0}))
        #print pre_dist
        #print post_dist
                
        #if question has a disagree expert response, negate the answers
        if header_pre[sem_year][q][3] == 'n': 
            pre_expert_dict[q] = pre_dist[1]+pre_dist[2] #All 1's and 2's are expert-like
            post_expert = post_dist[1]+post_dist[2]
            pre_nonexpert_dict[q] = pre_dist[4]+pre_dist[5] #All 4's and 5's are non-expertlike
            post_nonexpert = post_dist[4]+post_dist[5]
        else :
            pre_expert_dict[q] = pre_dist[5]+pre_dist[4]  #All 4's and 5's are expertlike
            post_expert = post_dist[5]+post_dist[4]
            pre_nonexpert_dict[q] = pre_dist[1]+pre_dist[2] # All 1's and 2's are nonexpertlike
            post_nonexpert = post_dist[1]+post_dist[2]
        pre_neutral_dict[q] = pre_dist[3]
#        post_neutral = post_dist[3]
        
        shift_expert_dict[q] = post_expert - pre_expert_dict[q]
#        shift_neutral_dict[q] = post_neutral - pre_neutral_dict[q]
        shift_nonexpert_dict[q] = post_nonexpert - pre_nonexpert_dict[q]
        
    #convert the dictionaries into Pandas Series type
    pre_expert_series = p.Series(pre_expert_dict)
    shift_expert_series = p.Series(shift_expert_dict)
    pre_nonexpert_series = p.Series(pre_nonexpert_dict)
    shift_nonexpert_series = p.Series(shift_nonexpert_dict)
    pre_neutral_series = p.Series(pre_neutral_dict)  
    dataframe_dict = {'pre_expert':pre_expert_series, \
                    'shift_expert':shift_expert_series, \
                    'pre_nonexpert':pre_nonexpert_series, \
                    'shift_nonexpert':shift_nonexpert_series,\
                    'pre_neutral':pre_neutral_series,\
                    'sem_year':sem_year}

    if for_categories == True:
        #Create a pre_series and a shift series for all the categories
        pre_expert_dict_cat = {}
        pre_neutral_dict_cat = {}
        pre_nonexpert_dict_cat = {}
        shift_expert_dict_cat = {}    
    #    shift_neutral_dict_cat = {}
        shift_nonexpert_dict_cat = {}
    
        cat_list = get_categories(sem_year)
        for cat in cat_list :
            q_cat = get_q_list(sem_year,qtype=qtype, category=cat)
            pre_expert_dict_cat[cat] = pre_expert_series[q_cat].sum()
            shift_expert_dict_cat[cat] = shift_expert_series[q_cat].sum()
            pre_nonexpert_dict_cat[cat] = pre_nonexpert_series[q_cat].sum()
            shift_nonexpert_dict_cat[cat] = shift_nonexpert_series[q_cat].sum()
            pre_neutral_dict_cat[cat] = pre_neutral_series[q_cat].sum()
        pre_expert_series_cat = p.Series(pre_expert_dict_cat)
        shift_expert_series_cat = p.Series(shift_expert_dict_cat)
        pre_nonexpert_series_cat = p.Series(pre_nonexpert_dict_cat)
        shift_nonexpert_series_cat = p.Series(shift_nonexpert_dict_cat)
        pre_neutral_series_cat = p.Series(pre_neutral_dict_cat)    
        dataframe_dict = {'pre_expert_cat':pre_expert_series_cat, \
                        'shift_expert_cat':shift_expert_series_cat,\
                        'pre_nonexpert_cat':pre_nonexpert_series_cat,\
                        'shift_nonexpert_cat':shift_nonexpert_series_cat,\
                        'pre_neutral_cat':pre_neutral_series_cat}
               
    return p.DataFrame(dataframe_dict)
 

#############~~~~~~~~~~~~ BASIC PLOTTING FUNCTIONS ~~~~~~~~~~############# 

def hist_with_err(ax,hist_data,data_err,width,data_series_num,ind,colour,scaled=False):
    '''makes a histogram with error bars
    ax              = axes
    datain          = data being used
    width           = width of the histogram bars
    data_series_num = for plotting interleaved hist, the data number 
                      (i.e. is it the first data set? Then input 0)
    ind             = index
    colour          = color of the bar you are plotting.
    '''  
#    hist_data, data_err = hist_process_data(datain,scaled=scaled)
    hist = ax.bar(ind+data_series_num*width,hist_data,width=width,color=colour,yerr=data_err,ecolor='k')
    py.ylim(ymin=0)
    if scaled == True:
        py.ylim(ymax=1)
    return hist

def plot_2d_hist(datarray, ax):
    #plotting 2d datarray plus annotation
    #CS = py.imshow(datarray,interpolation='nearest',origin='lower',extent=(0.5,5.5,0.5,5.5))
    dax = ax.imshow(datarray,interpolation='nearest',origin='lower',extent=(0.5,5.5,0.5,5.5))
    for x in range(1,6,1):
            for y in range(1,6,1):
                if datarray[y-1,x-1]!=0:
                    ax.annotate(str(int(datarray[y-1,x-1])),xy=(x,y),horizontalalignment='center',  #put the number of respondents who made that
                                verticalalignment='center',color = 'w',fontsize=12)                                          #particular shift in the corresponding box.
    py.set_cmap('gray_r')
    
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(dax, cax=cax)\
    #plt.colorbar(dax)
    #ax #Need to make ax active in order to return the correct set of axes
    return ax
    
   
def plot_gains_1D(ax,pre_shift_dataframe, df_name, sortby, offset,colour='r', \
                  exp_nonexp='expertlike', qtype='personal', categories=False, \
                  plot_title = True, text_labels = True, first = False) :
    """
    Generate the 1D bar chart plot for a set of questions or categories
    If sortby = 'pre', 'post', or 'shift' then sort the datasets given in the function.
    If sortby is a pandas.Series object, then sort by that series.
    """    
    if categories == False:
        pre_expert_series = pre_shift_dataframe['pre_expert']
        shift_expert_series = pre_shift_dataframe['shift_expert']
        pre_nonexpert_series = pre_shift_dataframe['pre_nonexpert']
        shift_nonexpert_series = pre_shift_dataframe['shift_nonexpert']
        pre_neutral_series = pre_shift_dataframe['pre_neutral']
        sem_year = pre_shift_dataframe['sem_year'][0]
    else:
        pre_expert_series = pre_shift_dataframe['pre_expert_cat']
        shift_expert_series = pre_shift_dataframe['shift_expert_cat']
        pre_nonexpert_series = pre_shift_dataframe['pre_nonexpert_cat']
        shift_nonexpert_series = pre_shift_dataframe['shift_nonexpert_cat']
        pre_neutral_series = pre_shift_dataframe['pre_neutral_cat']     
        
    num_matched_series = pre_expert_series + pre_neutral_series + pre_nonexpert_series
    
    if exp_nonexp == 'expertlike' :
        pre_series = pre_expert_series
        shift_series = shift_expert_series
    elif exp_nonexp == 'nonexpertlike':
        pre_series = pre_nonexpert_series
        shift_series = shift_nonexpert_series
    else :
        print("exp_nonexp set to invalid value.  Should be 'expertlike' or 'nonexpertlike'")
        print("Method failed.")
        return -1 

    #sort by the normalized responses (not total because num_matched can vary for different categories)        
    if isinstance(sortby,p.Series) :
        sort_series = sortby    
    elif sortby == 'pre' :
        sort_series = 1.0*pre_series/num_matched_series
    elif sortby == 'shift' :
        sort_series = 1.0*shift_series/num_matched_series
    elif sortby == 'post' :
        sort_series = 1.0*(pre_series + shift_series)/num_matched_series
    else :  #default is to sort by 'pre'
        sort_series = 1.0*pre_series/num_matched_series
#    print sort_series    
    sort_series.sort()
#    print sort_series

    ax.set_ylim(0,len(pre_series) + 1) #There are 30 questions
#    
#    #Add vertical grid lines    
#    ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')
#    print pre_series.index, num_matched_series.index, sort_series.index
    #loop over all the questions and make the plot
    counter = 1
    q_last = sort_series.index[-1]
    for q in sort_series.index :
#        num_matched = pre_expert_series[q] + pre_neutral_series[q] + pre_nonexpert_series[q]
        pre_norm = pre_series[q]*1.0/num_matched_series[q]
        shift_norm = shift_series[q]*1.0/num_matched_series[q]
        print(q + ", N = " + str(num_matched_series[q]) + ", pre_norm = " + str(pre_norm) + ", shift_norm = " + str(shift_norm))

        #plot the horizontal grid line        
        ax.plot([0,1],[counter,counter], '--', color='0.8')
        #plot the marker at the pre position      
        if q == q_last:
            circ=ax.plot([pre_norm], [counter+offset], 'o',color=colour,label=df_name)
        else:
            ax.plot([pre_norm], [counter+offset], 'o',color=colour)
        #plot the arrow if there is a nonzero shift        
        if shift_norm != 0.0 :        
            ax.arrow(pre_norm, counter+offset, shift_norm, 0, \
                     length_includes_head = True, head_width = 0.4, head_length = 0.015)
#        print "Pre_expert = " + str(pre_expert_series[q]) + "  Pre_nonexpert = " + str(pre_nonexpert_series[q]) + " num_matched = " + str(num_matched)
        #calculate the error bars on the pre-value        
        if exp_nonexp == 'expertlike' :
            pre_expert_series
#        print "fav_act = " + str(pre_expert_series[q]) + ", unfav_act = " + str(pre_nonexpert_series[q]) + ", num_matched = " + str(num_matched_series[q])
        expert_unc, nonexpert_unc = uncertainty_1D_fast(fav_act=pre_expert_series[q], \
                    unfav_act=pre_nonexpert_series[q], num_matched=num_matched_series[q])
#        print "expert_unc = " + str(expert_unc) + ", nonexpert_unc = " + str(nonexpert_unc)
        
        #Pick the correct uncertainty depending on whether expertlike or nonexpertlike is chosed        
        if exp_nonexp == 'expertlike' :
            uncertainty = expert_unc
        elif exp_nonexp == 'nonexpertlike' :
            uncertainty = nonexpert_unc
        
        uncertainty_norm = uncertainty/num_matched_series[q]
        
        sigma_scale = 1.95996 #gives the 95% confidence interval
        uncertainty_norm *= sigma_scale #scale uncertainty to a 95% confidence interval
        #print "expert_unc = " + str(expert_unc)
        #plot the error interval        
#        print "This is where it makes the error bar"  +str([[pre_norm - uncertainty_norm, pre_norm + uncertainty_norm],
#                [counter, counter]])      
        ax.plot([pre_norm - uncertainty_norm, pre_norm + uncertainty_norm], \
                [counter+offset, counter+offset],color=colour,lw=6,alpha=0.2 )        
        
        #Add the question text
        #title = str(pre_expert_series[q])+ ", "+ str(pre_nonexpert_series[q]) + "  " + header_pre[q][0]
        if first == True:
            if categories == False :   
                title = header_pre[sem_year][q]['Question Text']        
            elif categories == True :
                title = q + ", N = " + str(num_matched_series[q]) #This is just the category name
            if text_labels == True :
                ax.text(1.02, counter, title,fontsize=9,verticalalignment='center')
        
        counter = counter + 1
    ax.legend(loc=2)
    if exp_nonexp == 'expertlike' :    
        py.xlabel('Fraction of class with expert-like response')
    elif exp_nonexp == 'nonexpertlike' :    
        py.xlabel('Fraction of class with nonexpert-like response')

    py.subplots_adjust(bottom=0.08, left=.04, right=.99, top=.95, hspace=.1)
    if plot_title == True:
        if qtype == 'personal' :
            qtext = 'What do YOU think?'
        elif qtype == 'professional' :
            qtext = 'What would experimental physicists say about their research?'
        elif qtype == 'grade' :
            qtext = 'How important was this for earning a good grade?'
        elif qtype == 'practice' :
            qtext = 'How often did you engage in this practice?'
        py.suptitle(qtext +  '  N = '+str(num_matched_series[q]) + ", Showing " + exp_nonexp + " responses, sorting by " + sortby, )
    py.show()
    
    return ax
        
############~~~~~~~~~~~~CORRELATION TABLES~~~~~~~~~~##############     

def expertlike_grade_level_correlation(datain):
    global course_data
    expertlike = score_dist_process_data(datain,1.)
    class_level = []
    for stud in datain.index:
        course=datain.loc[stud,'Class']
        course_row = course_data[course_data['Instructor_html']==course]['Alg_Calc_Other_Num']
        ind = course_row.index[0]
        level = course_row.loc[ind]
        class_level.append(level)
    corr = pearsonr(expertlike,class_level)
    print('expertlike, course level correlation =', corr)
    
    course_list = list(set(datain['Class']))
    course_level = []
    
    print('course: average, stdev')
    for course in course_list:
        data_course = data_query(datain, Class = course)
        expertlike_course = score_dist_process_data(data_course,1.)
        ave_expertlike = np.average(expertlike_course)
        stdev_expertlike = np.std(expertlike_course)
        print(course, ': ', ave_expertlike, ', ', stdev_expertlike)    
        courselevel = get_class_level(course)[0]
        course_level.append(courselevel)
    
    courses=data_query(course_data, Instructor_html = course_list)
    upper_division = list(set(courses[courses['Alg_Calc_Other_Letter']=='O']['Instructor_html']))
    calculus_intro = list(set(courses[courses['Alg_Calc_Other_Letter']=='C']['Instructor_html']))
    non_calculus_intro = list(set(courses[courses['Alg_Calc_Other_Letter']=='A']['Instructor_html']))
    
    courses_list = [upper_division, calculus_intro, non_calculus_intro]
    courses_name = ['upper div', 'calc intro', 'non-calc intro']
    
    for level in range(len(courses_list)):
        if len(courses_list[level])>0:
            level_subset = data_query(datain, Class = courses_list[level])
            expert_like = score_dist_process_data(level_subset,1.)
            ave_expert_like = np.average(expert_like)
            stdev_expert_like = np.std(expert_like)
            print(courses_name[level], 'ave =', ave_expert_like, 'stdev =', stdev_expert_like)      
    return

def grade_practice_correlation(datain):
    sem = list(set(data_in['Semester']))[0]
    year = list(set(data_in['Year']))[0]
    sem_year=sem[0:2]+year[2:4]    
    grade_q_list = get_q_list(sem_year,type='grade')
    corr_list = []
    p_values_list = []
    d=data_query(datain,PrePost='Post')
    for q in grade_q_list:
        x=d[q]
        r=q.replace('c','d')
        y=d[r]
        for l in x.index:
            if isinstance(x[l],str):
                x[l]=int(x[l])
        for l in y.index:
            if isinstance(y[l],str):
                y[l]=int(y[l])
        corr = pearsonr(x,y)
        corr_list.append(corr[0])
        p_values_list.append(corr[1])
    average_corr = np.average(corr_list)
    stdev_corr = np.std(corr_list)
    return average_corr, stdev_corr
        
def q1_q2_correlation_stats(datain,qtype1='grade',qtype2='practice', save_table=False):
    """
    Returns a data frame with the Fraction of students answering on same on
    both the grade and practice question AND the Pearson r coefficient between
    grade and practice coefficients.
    """
    sem = list(set(data_in['Semester']))[0]
    year = list(set(data_in['Year']))[0]
    sem_year=sem[0:2]+year[2:4]
    grade_q_list = get_q_list(sem_year,qtype=qtype1)
    corr_list = []
    p_values_list = []
    diag_list = []
    qtype1_text_list = []
    qtype2_text_list = []
    d=data_query(datain,PrePost='Post')
    for q in grade_q_list:
        x=d[q]  #a column of the grade questions
        r,inlist=change_q_type(q,qtype2)  #convert a grade into a practice question
        if inlist==True:
            y=d[r]  #A matching column for the practice question
    
            diag = 0 #counter for number of elements on the diagonal        
            for l in x.index:  #if there are strings in the number column, convert them to numbers.
                if isinstance(x[l],str):
                    x[l]=int(x[l])
                if isinstance(y[l],str):
                    y[l]=int(y[l])
                if header_post[q][3]=='n' and header_post[r][3]=='p':
                    x=-(x-3)+3
                if header_post[q][3]=='p' and header_post[r][3]=='n':
                    y=-(y-3)+3                
                if y[l]==x[l] :  #if an element is on the diagonal, increment diag
                    diag = diag + 1
            corr = pearsonr(x,y)  #pearsonr returns the correlation coeff and p value
            corr_list.append(corr[0])
            p_values_list.append(corr[1])
            diag_list.append(1.0*diag/len(x))
            
            #Question text
            qtype1_text = header_post[q][0]
            qtype2_text = header_post[r][0]
            qtype1_text_list.append(qtype1_text)
            qtype2_text_list.append(qtype2_text)
        else:
            print((q+" does not have a "+qtype2+" equivalent."))
    corr_series = p.Series(corr_list, index=grade_q_list)
    diag_series = p.Series(diag_list, index=grade_q_list)
    p_values_series = p.Series(p_values_list, index=grade_q_list)
    qtype1_text_series = p.Series(qtype1_text_list, index=grade_q_list)
    qtype2_text_series = p.Series(qtype2_text_list, index=grade_q_list)
    
    corr_stats = p.DataFrame({"Pearson_corr":corr_series, "Fraction_diag":diag_series,
                              "P-values":p_values_series, "Question Type1 Text":qtype1_text_series,
                              "Question Type2 Text": qtype2_text_series})
    
    if save_table == True :
        full_dir = _get_new_table_dir("Grade_Practice_Correlation_Table")        
        filename = "Grade_practice_correlation_table.csv"
        corr_stats.to_csv(full_dir + filename) 
        
    return corr_stats
    
def grade_shift_correlation_stats(datain,save_table=False):
    """
    Returns a data frame with the Fraction of students answering on same on
    both the grade and practice question AND the Pearson r coefficient between
    grade and practice coefficients.
    """
    sem = list(set(data_in['Semester']))[0]
    year = list(set(data_in['Year']))[0]
    sem_year=sem[0:2]+year[2:4]
    grade_q_list = get_q_list(sem_year,qtype='grade')
    corr_list = []
    p_values_list = []
    diag_list = []
    grade_q_text_list = []
    shift_q_text_list = []
    pre=data_query(datain,PrePost='Pre')
    post = data_query(datain,PrePost = 'Post')
    num_matched = len(pre)
    if num_matched==0: print("no matched responses");return
    for q in grade_q_list:
        x=[]
        y=[]
        r,inlist=change_q_type(q,'personal')  #convert a grade into a practice question
        if inlist == True:
            for studid in pre['SID_unique']:
                preresponse = data_query(pre,SID_unique=studid)[r]
                postresponse = data_query(post,SID_unique=studid)[r]
                shift = float(postresponse.values[0]) - float(preresponse.values[0])
                if header_post[r][3]=='n':
                    shift = -shift
                y.append(shift)
                grade = data_query(post,SID=studid)[q]
                g_response = float(grade.values[0])
                if header_post[q][3]=='n':
                    g_response= -(g_response-3)+3
                x.append(g_response)
            
            diag = 0 #counter for number of elements on the diagonal        
            for l in range(len(x)):  
                if y[l]==x[l] :  #if an element is on the diagonal, increment diag
                    diag = diag + 1
            corr = pearsonr(x,y)  #pearsonr returns the correlation coeff and p value
            corr_list.append(corr[0])
            p_values_list.append(corr[1])
            diag_list.append(1.0*diag/len(x))
            
            #question text
            grade_q_text = header_post[q][0]
            shift_q_text = header_post[r][0]
            grade_q_text_list.append(grade_q_text)
            shift_q_text_list.append(shift_q_text)
        else:
            print((q+" does not have a 'personal' equivalent"))
    corr_series = p.Series(corr_list, index=grade_q_list)
    p_value_series = p.Series(p_values_list,index=grade_q_list)
    diag_series = p.Series(diag_list, index=grade_q_list)
    grade_q_series = p.Series(grade_q_text_list, index = grade_q_text_list)
    shift_q_series = p.Series(shift_q_text_list, index = shift_q_text_list)
    
    corr_stats = p.DataFrame({"P-value":p_value_series,"Pearson_corr":corr_series,
                              "Fraction_diag":diag_series, "Grade Question text": grade_q_series,
                              "Shift Question text": shift_q_series})
    
    if save_table == True :
        full_dir = _get_new_table_dir("Grade_Shift_Correlation_Table")        
        filename = "Grade_shift_correlation_table.csv"
        corr_stats.to_csv(full_dir + filename) 
        
    return corr_stats
       
################~~~~~~~~~~  OTHER  ~~~~~~~~~~~~##################
        
def course_goals(datain,save_table=False):
    """
    Make a pandas DataFrame with columns for question text, mean, std devation.
    Analyzes just the questions about earning a good grade.    
    """
    #sem = list(set(datain.loc[:,'Semester']))[0]
    #year = list(set(datain.loc[:,'Year']))[0]
    #sem_year = sem[0:2]+year[2:4]
    #get a list of questions that are grade questions
    q_grade_list = []
    for cols in data:
        if cols[0]=='q' and cols[3]=='c' :
            q_grade_list.append(cols)
    
    #course = list(set(datain['Class']))[0]
    #print q_grade_list            
            
    d = data_query(datain,PrePost='Post')
    data_sub = d.reindex(columns=q_grade_list)
    data_sub = data_sub.applymap(float)  #Convert all the integer data to float    
    data_sub[data_sub == 0] = np.NaN #Set the no answers to nan so they are ignored in the calculations
    
    #print "printing data_sub"    
    #print data_sub
    
    #Temporary arrays to build up the question names, mean
    header_sub = header_post.reindex(columns=q_grade_list)
    #print "header_sub = "
    #print header_sub
    q_list = header_sub.ix['Question Text']
    #print(q_list)
    mean_list = data_sub.mean()  #Mean of each column
    #print "mean_list"
    #print(mean_list)
    std_list = data_sub.std()   #Std.dev. of each column
    count_list = data_sub.count() #Number of valid responses used for calvulating std dev of mean
    std_mean = std_list/count_list.apply(np.sqrt)
    
    #Clip the repetative text off the beginning of each question
    trunc = lambda s : s.replace('How important for earning a good grade in this class was ','...')
    q_list = q_list.apply(trunc)
    
    #Combine all the Series data into a DataFrame
    grade_dict = {'Question_Text':q_list, 'mean':mean_list, 'std_mean':std_mean}
    grade_frame = p.DataFrame(grade_dict)
    #Sort the frame according to the mean column    
    grade_frame = grade_frame.sort(columns='mean',ascending=False)
    
     #If save_table == True, save a csv of the table
    if save_table == True :
        full_dir = _get_new_table_dir("Grade_Table")
        filename = "Grade_table.csv"
        #filename = "Grade_table_"+ course + ".csv"
        grade_frame.to_csv(full_dir + filename)
    
    return grade_frame
