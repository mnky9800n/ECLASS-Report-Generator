# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 15:38:44 2013

@author: Takako
"""
import pandas as p                                                                      #import data

#_common_directory = ''
#_graph_directory = ''
#_table_directory = ''
#_data_directory = ''


#Header Files
#Header files for IDs are no longer needed with Qualtrics Data
#_header_IDs_file = 'header_IDs.csv'                 # IDs
#_pre_header_file = 'header_pre_results.csv'         # Pre results
_pre_header_file = 'header_pre_qualtrics.csv'         # Pre results
#_post_header_file = 'header_post_results.csv'       # Post results
_post_header_file = 'header_post_qualtrics.csv'       # Post results
_class_meta_data_file = 'Class_Meta_data.csv'       # class meta data
course_data = 0

def load_meta_data(filename) :
    global course_data
    """
    Assumes a simple CSV file with columns about the course
    """
    course_data = p.read_csv(filename,index_col=None,dtype={'Directory':object}) #Load in course meta data

def load_headers(header_dir, pre_header_file, post_header_file) :
    global header_pre, header_post

    #Import the 2 header files
    header_pre = p.read_csv(header_dir + pre_header_file, index_col = 0) #Load in the header as a pandas frame
    header_post = p.read_csv(header_dir + post_header_file, index_col = 0) #Load in the header as a pandas frame

def initialize_data_Qualtrics(data_dir, pre_file, post_file) :
    """
    Typically run after load_meta_data() and get the directory and filenames from the meta_data
    Also, run after load_headers()
    """
    global data, header_pre, header_post, q_guide, _common_directory, \
            _graph_directory, _table_directory, _data_directory


    # filepaths = {}
    # filepaths['_common_directory'] = data_dir
    # filepaths['_graph_directory'] = data_dir + "graphs\\"
    # filepaths['_table_directory'] = data_dir + "table\\"

    #import the data
    data_pre = p.read_csv(data_dir+pre_file,names = header_pre.columns,index_col=False,skiprows=2)
    data_post = p.read_csv(data_dir+post_file,names = header_post.columns,index_col=False,skiprows=2)

    data_pre.insert(loc=0, column='PrePost', value = 'Pre') # insert a pre/post column
    data_post.insert(loc=0, column='PrePost', value='Post') # insert a pre/post column

    data = p.concat([data_pre,data_post],ignore_index=True)  # combine pre and post into a single data frame
    data_dict = {'data':data,'data_pre':data_pre, 'data_post':data_post, 'header_pre': header_pre,\
                 'header_post' : header_post}

    return data_dict


def initialize_data(semester, year, user):
    global data, header_pre, header_post, q_guide, categories, _common_directory, \
            _graph_directory, _table_directory, _data_directory, course_data
    
    filepaths = get_file_paths(semester, year, user)
    
    _common_directory = filepaths['_common_directory']
    _graph_directory = filepaths['_graph_directory']
    _table_directory = filepaths['_table_directory']
    _data_directory = filepaths['_data_directory']
    
    #_pre_IDs_file=filepaths['_pre_IDs_file']
   # _post_IDs_file=filepaths['_post_IDs_file']
    _pre_data_file=filepaths['_pre_data_file']
    _post_data_file=filepaths['_post_data_file']
    
    #Import the 3 header files    
    ##header_IDs = p.read_csv(_data_directory + _header_IDs_file) #Load in the IDs header
    header_pre = p.read_csv(_data_directory + _pre_header_file, index_col = 0) #Load in the header as a pandas frame
    header_post = p.read_csv(_data_directory + _post_header_file, index_col = 0) #Load in the header as a pandas frame
    
    #Import class meta data
    #course_data = p.read_csv(_data_directory + _class_meta_data_file,index_col=None) #Load in course meta data
           
    #Import the data
   ##Pre_IDs = p.read_csv(_data_directory+_pre_IDs_file,names = header_IDs.columns, index_col=None,dtype={'SID':object})
    # index_col=None so that you can set the index and also merge on those columns.
    # dtype={...} is forcing SIDs to be strings because sometimes the SIDs in the csv files can 
    # be considered as strings or floats depending on whats actually in the file. 
    Pre_results = p.read_csv(_data_directory+_pre_data_file,names = header_pre.columns,index_col=False,skiprows=2)
    #Post_IDs = p.read_csv(_data_directory+_post_IDs_file,names = header_IDs.columns, index_col=None,dtype={'SID':object})
    Post_results = p.read_csv(_data_directory+_post_data_file,names = header_post.columns,index_col=False,skiprows=2)

    
   ##Pre_IDs = Pre_IDs.set_index(['Institution','Time','Date','Class','Section'])

    """
    in order to merge the data and IDs they have to have matching indices.  This is accomplished by giving hte IDs and
    data matching indices using the set_index function and then merging.  This step is unncessary since there is only
    one data file as downloaded from qualtrics.
    """
    #Pre_results = Pre_results.set_index(['Institution','Time','Date','Class','Section'])    #Set a multi-index usingthe column names that are
    ##Post_IDs = Post_IDs.set_index(['Institution','Time','Date','Class','Section'])          #duplicated in both the ID and results
    #Post_results = Post_results.set_index(['Institution','Time','Date','Class','Section'])  #files.

    #don't need to merge hte data_pre with Pre_IDs since it is all one file in qualtrics
    #data_pre = p.merge(Pre_IDs,Pre_results, left_index = 'True', right_index = 'True') #the columns that show up in IDs shows up on the left
    #data_pre = data_pre.reset_index()
    ###data_post = p.merge(Post_IDs,Post_results, left_index = 'True', right_index = 'True')
    ###data_post = data_post.reset_index()
    
    data_pre = Pre_results
    data_post = Post_results
    data_pre.insert(loc=0, column='PrePost', value = 'Pre') # insert a pre/post column
    data_post.insert(loc=0, column='PrePost', value='Post') # insert a pre/post column


    data = p.concat([data_pre,data_post],ignore_index=True)  # combine pre and post into a single data frame
    #data = data.drop_duplicates()                               # drop duplicated rows
   # to_drop = drop_empty_rows(data)                             # get the rows to drop
    #data = data.drop(to_drop)                                   # cleaned up data set
    
    #data_dict = {'data':data, 'course_data':course_data, 'header_pre': header_pre, \
    #        'header_post': header_post, 'filepaths': filepaths}

    data_dict = {'data':data,'data_pre':data_pre, 'data_post':data_post, 'header_pre': header_pre,'header_post' : header_post,
            'filepaths': filepaths}

    return data_dict


    
    
def get_file_paths(semester, year, user):
    filepaths = {}  # a dictionary that allows a more readable access to file paths.
    
    if semester == 'Fall' and year == '2012':
        _pre_IDs_file = 'E-CLASS-Pre-Fa12_IDs_2012-12-19-CLEAN.csv'
        _post_IDs_file = 'E-CLASS-Post-Fa12_IDs_2012-12-19-CLEAN.csv'
        _pre_data_file = 'E-CLASS-Pre-Fa12_results_2012-12-19_CLEAN.csv'
        _post_data_file = 'E-CLASS-Post-Fa12_results_2012-12-19-CLEAN.csv'
        #Set Ben directory
        if user == 'Ben':
            _common_directory = 'C:\\Users\\Ben\\Dropbox\\E-CLASS\\Analysis\\Fa2012_E-CLASS\\'
            _graph_directory = _common_directory + "graphs\\"
            _table_directory = _common_directory + "tables\\"
            _data_directory = _common_directory + 'Clean data\\'
        #Set Takako directory
        elif user == 'Takako' :
            _common_directory = '/Users/Takako/Dropbox/E-CLASS/Analysis/Fa2012_E-CLASS/'
            _graph_directory = _common_directory + "graphs/"
            _table_directory = _common_directory + "tables/"
            _data_directory = _common_directory + 'Clean data/'
            
    elif semester == 'Spring' and year == '2013':                
        _pre_IDs_file = 'E-CLASS-Pre-Sp13_IDs_CLEAN.csv'
        _post_IDs_file = 'E-CLASS-Post-Sp13_IDs_CLEAN.csv'
        _pre_data_file = 'E-CLASS-Pre-Sp13_results_CLEAN.csv'
        _post_data_file = 'E-CLASS-Post-Sp13_results_CLEAN.csv'
        #Set Ben directory
        if user == 'Ben':
            _common_directory = 'C:\\Users\\Ben\\Dropbox\\E-CLASS\\Analysis\\Sp2013_E-CLASS\\'
            _graph_directory = _common_directory + "graphs\\"
            _table_directory = _common_directory + "tables\\"
            _data_directory = _common_directory + 'Clean data\\'
        #Set Takako directory
        elif user == 'Takako' :
            _common_directory = '/Users/Takako/Dropbox/E-CLASS/Analysis/Sp2013_E-CLASS/'
            _graph_directory = _common_directory + "graphs/"
            _table_directory = _common_directory + "tables/"
            _data_directory = _common_directory + 'Clean data/'

    elif semester == 'Spring' and year == '2015':
        _pre_data_file = 'ECLASS_Survey_Pre__Fall_2014__CU_PHYS_1140.csv'
        _post_data_file = 'ECLASS_Survey_Post__Fall_2014__CU_PHYS_1140.csv'
        #Set Ben directory
        if user == 'Ben':
            #_common_directory = 'C:\\SugarSync\\Ben\\RIT\\Research\\E-CLASS\\Python Report Generation\\Spring 2015\\'
            _common_directory = "C:\\Users\\bmzsps\\Repos\\e-class-qualtrics-SP2015\\Spring 2015\\"
            _graph_directory = _common_directory + "graphs\\"
            _table_directory = _common_directory + "tables\\"
            _data_directory = _common_directory + 'Qualtrics Data\\'
        #Set Takako directory
        # elif user == 'Takako' :
        #     _common_directory = '/Users/Takako/Dropbox/E-CLASS/Analysis/Sp2013_E-CLASS/'
        #     _graph_directory = _common_directory + "graphs/"
        #     _table_directory = _common_directory + "tables/"
        #     _data_directory = _common_directory + 'Clean data/'
            
    ##filepaths['_pre_IDs_file'] = _pre_IDs_file
    ##filepaths['_post_IDs_file'] = _post_IDs_file
    filepaths['_pre_data_file'] = _pre_data_file
    filepaths['_post_data_file'] = _post_data_file
    filepaths['_common_directory'] = _common_directory
    filepaths['_graph_directory'] = _graph_directory
    filepaths['_table_directory'] = _table_directory
    filepaths['_data_directory'] = _data_directory
    
    return filepaths

def drop_empty_rows(datain):
    '''This function drops all of the data rows that have 0s for all of the questions.
    Used only in initialize_data.'''
    todrop=[]                                                   #initialize empty list
    column_names = datain.columns
    q_list=[]
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
        elif datain.ix[response,'Class'] == 'empty':           #if inputted response doesn't put in a class, drop the row.
            todrop.append(response)
    return todrop

# ---------------------------------------NOTE---------------------------------------#
#If the code gets caught up on either 'merge' lines, check to make sure that there are the same
#number of columns in the header and corresponding data/ID file. You can check generally in Excel
#but if it seems like there are the same number of columns in Excel for both the header file
#and the IDs/results file, and it still gets caught up on that line, sometimes there might be 
#an extra 'column' if each line ends in a comma. Rather than deleting every line-ending comma
#just create an extra column in the header file by adding a comma at the end of the header line
