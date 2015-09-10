# -*- coding: utf-8 -*-
"""
Created on Wed Apr 03 15:34:13 2013

@author: Ben
"""

import Sp15_report_plots_v1 as P
p = P.F.p #pandas
import os 
import datetime as dt
import shutil

#fake data

#data = p.Series({'CLASS_NAME':'Intro Physics', \
#                 'INSTITUTION':'Univ. of Colorado', \
#                 'SEMESTER_YEAR':'Fall 2012'})

_user = 'Ben'
#_user = 'Takako'

if _user == 'Ben':
    _directory_common = "C:\\SugarSync\\Ben\\RIT\\Research\\E-CLASS\\Python Report Generation\\"
   # _directory_common = "C:\\Users\\Ben\\Dropbox\\E-CLASS\\"
    _directory_html = _directory_common + "Reports to Instructors\\"
elif _user == 'Takako':
    _directory_common = "/Users/Takako/Dropbox/E-CLASS/"
    _directory_html = _directory_common + "Reports to Instructors/"  

_filename_template = _directory_html + "E-CLASS_Report_Template_Sp13.html"


def make_all_reports() :

    course_list = P.F.data['Class'].value_counts()
    course_list = course_list.drop('empty')  #drop the 'empty' class
    course_list = course_list[course_list > 3] #only pick classes with more than 3 responses
#    course_list = course_list[course_list < 62]    #Use this to restrict the courses of interest (debugging)
    print(course_list)
    today = dt.datetime.now()
    if _user == 'Ben':
        _directory_date = _directory_html + today.strftime("%Y-%m-%d %H.%M.%S %p") + '\\'    
    elif _user == 'Takako':
        _directory_date = _directory_html + today.strftime("%Y-%m-%d %H.%M.%S %p") + '/' 
    
    for c in course_list.index :
        if c != 'Fudan_University_All_Class':
            print(c + ", N = " + str(course_list[c]))
            make_report(class_name = c, directory=_directory_date)
            P.py.close('all')

def save_clean_data(course_data_filepath) :
    """
    course_data_filepath = path to a summary CSV file that lists all courses at a particular level
    """
    P.F.Import.load_meta_data(course_data_filepath)
    course_data = P.F.Import.course_data

    header_dir = "C:\\Users\\bmzsps\\Repos\\e-class-qualtrics-SP2015\\Data\\Header\\"
    pre_header_file = "header_pre_qualtrics_auto.csv"
    post_header_file = "header_post_qualtrics_auto.csv"
    P.F.Import.load_headers(header_dir, pre_header_file, post_header_file)

    level_data_list = []

    for i in range(0,len(course_data)) :
        single_course_data = P.F.Import.course_data.irow(i)
        data_dir = single_course_data["Directory"]

        #append the directory divider if it isn't already there
        if data_dir[-1] != "\\" :
            data_dir += "\\"

        pre_filename = single_course_data["Pre_Filename"]
        post_filename = single_course_data["Post_Filename"]
        print("data_dir = \'{}\'".format(data_dir))
        # create the clean, matched data set for one institution.
        P.F.initialize_data_clean_qualtrics(data_dir, pre_filename, post_filename, reload_data=True)
        #level_data_list.append(P.F.data.copy())
        p.to_pickle(P.F.data, data_dir + "data.pkl" )
        p.to_pickle(P.F.data_raw_nodups, data_dir + "data_raw_no_dups.pkl")

def make_level_data(course_data_filepath, course_index) :
    """
    Loads already generated picked dataframes for each of the
    courses listed in course_data_filepath.
    All pickled data files are named "data.pkl"
    """
    P.F.Import.load_meta_data(course_data_filepath)
    course_data = P.F.Import.course_data

    header_dir = "C:\\Users\\bmzsps\\Repos\\e-class-qualtrics-SP2015\\Data\\Header\\"
    pre_header_file = "header_pre_qualtrics_auto.csv"
    post_header_file = "header_post_qualtrics_auto.csv"
    P.F.Import.load_headers(header_dir, pre_header_file, post_header_file)

    data_level_list = []

    for i in range(0,len(course_data)) :

        #skip the reading of data for the course_index so it isn't in comparison level data set.
        if i == course_index :
            continue

        single_course_data = P.F.Import.course_data.irow(i)
        data_dir = single_course_data["Directory"]

        #append the directory divider if it isn't already there
        if data_dir[-1] != "\\" :
            data_dir += "\\"

        d = p.read_pickle(data_dir + "data.pkl")

        data_level_list.append(d.copy())

    data_level = p.concat(data_level_list,ignore_index=True)
    return data_level

def make_course_data(course_data_filepath, course_index):

    P.F.Import.load_meta_data(course_data_filepath)
    course_data = P.F.Import.course_data

    header_dir = "C:\\Users\\bmzsps\\Repos\\e-class-qualtrics-SP2015\\Data\\Header\\"
    pre_header_file = "header_pre_qualtrics_auto.csv"
    post_header_file = "header_post_qualtrics_auto.csv"
    P.F.Import.load_headers(header_dir, pre_header_file, post_header_file)

    single_course_data = P.F.Import.course_data.irow(course_index)
    data_dir = single_course_data["Directory"]

    #append the directory divider if it isn't already there
    if data_dir[-1] != "\\" :
        data_dir += "\\"

    data_course = p.read_pickle(data_dir + "data.pkl")
    data_raw_no_dups = p.read_pickle(data_dir + "data_raw_no_dups.pkl")
    return (data_course, data_raw_no_dups)


def make_reports_qualtrics_unpickle(course_data_filepath, template_filepath,plotting=True) :

    P.F.Import.load_meta_data(course_data_filepath)
    n_classes = len(P.F.Import.course_data)
    print("number of courses = {}".format(n_classes))

    for i in range (0,n_classes) :
        data_course, data_raw_no_dups = make_course_data(course_data_filepath,i)
        data_level = make_level_data(course_data_filepath,i)
        make_report_qualtrics(data_course, data_raw_no_dups ,data_level, course_data_filepath,i,template_filepath,plotting)






def make_report_qualtrics(d, d_unmatched, data_level,course_data_filepath,course_row_index, template_filepath,plotting=True) :
    """
    Run the run_qualtrics() function to produce the entire set of saved plots.
    """

    #import the HTML template
    template = open(template_filepath, 'r')
    html_template_string = template.read()

    print("course_row_index = {} (make_report_qualtrics)".format(course_row_index))

    #generate all the plots and metadata
    template_fill_data = P.run_qualtrics(d, d_unmatched, data_level, course_data_filepath, course_row_index, plotting)

    #create a new HTML document
    html_new_report = html_template_string #initialize the new report prior to subsituting in content
    for var in list(template_fill_data.keys()) :
#        print var
        html_new_report = html_new_report.replace('{'+var+'}',template_fill_data[var])


    template.close()
    single_course_data = P.F.Import.course_data.irow(course_row_index)
    _directory_report = single_course_data['Directory']
    if _directory_report[-1] != '\\' :
        _directory_report += '\\'
    _course_title = single_course_data['Course_Title']
    _course_number = single_course_data['Course_Number']
    _ugly_name = single_course_data['Ugly_name']

    #Create and save the new HTML report file

    _filename_report = _directory_report + 'ECLASS_Report_'+ _ugly_name + '.html'
    report = open(_filename_report,'w')
    report.write(html_new_report)
    report.close()

def make_report(class_name = 'Western_Michigan_University_Physics_1140_General_Physics_1_Lab',directory='empty' ):
       
#    class_name = 'Western_Michigan_University_Physics_1140_General_Physics_1_Lab'
        
    #make a directory with the date and time
    if directory == 'empty' :    
        today = dt.datetime.now()
        if _user == 'Ben':
            _directory_date = _directory_html + today.strftime("%Y-%m-%d %H.%M.%S %p") + '\\'
        elif _user == 'Takako':
            _directory_date = _directory_html + today.strftime("%Y-%m-%d %H.%M.%S %p") + '/'
    else :
        _directory_date = directory
    
    if os.path.isdir(_directory_date) == False:
        os.mkdir(_directory_date)
        
    #make a subdirectory for the report for the school.  
    #The HTML file is saved within this directory
    if _user == 'Ben':
        _directory_report = _directory_date + P.get_readable_institution(class_name) + ' ' + P.get_readable_course_name(class_name) + '\\'
    elif _user == 'Takako':
        _directory_report = _directory_date + P.get_readable_institution(class_name) + ' ' + P.get_readable_course_name(class_name) + '/'
    if os.path.isdir(_directory_report) == False:
        os.mkdir(_directory_report)
        
    #Create a sub-sub-directory for all the plots and maybe tables.
    #I am not sure how to best incorporate the tables at this point.  Does pandas
    #have an HTML export for the pandas DataFrames?    
    if _user == 'Ben':
        _directory_graphics = _directory_report + 'Graphics\\'
    elif _user == 'Takako':
        _directory_graphics = _directory_report + 'Graphics/'
    if os.path.isdir(_directory_graphics) == False:
        os.mkdir(_directory_graphics)
    
    #Make the graphics
    #make_graphics(data=[], directory_graphics = _directory_graphics)
    
    #Save the HTML report within the subdirectory for the course
    #Save hte accompanying graphics within the subdirectory for course\graphics
    
    #Load the HTML Template
    template = open(_filename_template, 'r')
    
    #Make all the graphics and get the info from the data set
    template_fill_data = P.run(class_name = class_name, graphics_directory = _directory_graphics)    
    print(template_fill_data)
    
    if template_fill_data == 'error' :
        return 'error'
    
   
    html_template_string = template.read()
    html_new_report = html_template_string #initialize the new report prior to subsituting in content
    for var in list(template_fill_data.keys()) :
#        print var 
        html_new_report = html_new_report.replace('{'+var+'}',template_fill_data[var])
         
#        print template_fill_data[var]
#    grade_table_html = P.run()    
#    
#    html_new_report = html_new_report.replace('{GRADE_TABLE}',grade_table_html)
                        
    template.close()
    
#    print html_new_report    
    
    #Create and save the new HTML report file
    _filename_report = _directory_report + 'ECLASS_Report_'+ P.get_readable_course_name(class_name) + '.html'
    report = open(_filename_report,'w')
    report.write(html_new_report)
    report.close()

def make_graphics(data, directory_graphics):
    
    #location for the test graphics
    if _user == 'Ben':
        directory_test_graphics = "C:\\Users\\Ben\\Dropbox\\E-CLASS\\Reports to Instructors\\Graphics\\"
    elif _user == 'Takako':
        directory_test_graphics = "/Users/Takako/Dropbox/E-CLASS/Reports to Instructors/Graphics/"
    #make the 2D histogram
    shutil.copy(directory_test_graphics + "Single_Question_2D_pre_post_Hist.png", \
                directory_graphics )
    #Make the interleaved histograms
    shutil.copy(directory_test_graphics + "Single_Question_Interleaved_pre_post_Hist.png", \
                directory_graphics )
    #Make the pre post shift for one question
    shutil.copy(directory_test_graphics + "Single_Question_pre_post_change.png", \
                directory_graphics )
    #Make the pre post shift for all questions
    shutil.copy(directory_test_graphics + "All_Questions_pre_post_change.png", \
                directory_graphics)
    #Make the pre post shift for all categories
    shutil.copy(directory_test_graphics + "All_Categeories_pre_post_change.png", \
                directory_graphics)
