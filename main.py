#import Questions
import Questions
import UtilitiesForPlotting as utilities
import DataCleaner
#import BuildReport
import os
import pandas as pd
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import shutil
import jinja2
import timeit
import eclass_item_plot as item_plot

class NoCourseDataError(Exception):
    pass

class NoArgsError(Exception):
    pass


def load_pre_post_data(pre, post):
    """
    loads cleaned data and returns a pandas dataframe
    of the merged data.
    """
    predata = pd.read_csv(pre)#'preMunged_Aggregate_Data.csv')
    postdata = pd.read_csv(post)#'postMunged_Aggregate_Data.csv')

    return predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])

def get_sys_args():
    """
    checks for correct number of sys args present
    in command line string. Returns error if missing
    data.
    """
    args = [arg for arg in sys.argv]

    if len(args) == 5:#4: apparently main.py is an argument too. didn't know that.
        return args
    else:
        raise NoArgsError("""
        You must provide 4 data source files
        as CSVs in the following order:
        pre-historical data
        post-historical data
        course data directory
        instructor survey dat
        You have provided {length} arguments instead.
        These arguments are: {args}
        """.format(length=len(args), args=str(args)))

def get_GMT_year_month():
    """
    returns GMT year and month as a string
    """
    t = time.gmtime()
    return str(t.tm_year) + '_' + str(t.tm_mon)

def add_date(id):
    return id + '_' + get_GMT_year_month()

# TODO: create table 1 function



if __name__ == "__main__":

    timing = True
    show_figs = True

    if timing == True:
        start = timeit.default_timer()

    # object instantiation (not neccessary)
    Questions = Questions.Questions()

    # directory parameters
    parent_dir = os.getcwd() + '\\data'


    # plotting parameters
    DPI = 60
    expectedRows_Q49 = [1.,2.,3.,4.,5.,6.]
    questionAnswers = {1.0: 'Physics', 2.0: 'Chemistry', 3.0: 'Biochemistry', 4.0: 'Biology', 5.0: 'Engineering', 6.0: 'Engineering Physics', 7.0: 'Astronomy', 8.0: 'Astrophysics', 9.0: 'Geology/geophysics', 10.0: 'Math/Applied Math', 11.0: 'Computer Science', 12.0: 'Physiology', 13.0: 'Other Science', 14.0: 'Non-science Major', 15.0: 'Open option/Undeclared'}
    expectedRows_Q47 = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,15.]

    main, pre_hist, post_hist, coursedir, instructordata = get_sys_args() #wtf is main?

    
    # clean all data from current semester and prepare for plotting
    DataCleaner.cleanDataPipeline(coursedir)

    # load raw data into dataframes
    course_raw_data = load_pre_post_data(pre='preMunged_Aggregate_Data.csv'
                                   ,post='postMunged_Aggregate_Data.csv')
    historical_raw_data = load_pre_post_data(pre=pre_hist, post=post_hist)

    # get all unique course ideas, append the current GMT year and month
    courseIDs = list(set(course_raw_data.courseID.values))
    courseIDs_Date = [m for m in map(add_date, courseIDs)]

    #make historical itemized data plot
    hist_item_data = item_plot.make_eclass_item_dataframe(df=historical_raw_data)

    hist_grades = utilities.expertLikeResponseDataFrame(rawdata_df=historical_raw_data
                                                    , columnIDs=Questions.post_GradeQuestionIDs
                                                    , CI_Calculator=utilities.confidenceInterval
                                                    , grades=True)
    hist_grades.columns = ['cipost','fracpost']

    #course_item_data = item_plot.make_eclass_item_dataframe(df=course_raw_data)

    qids_WHAT = item_plot.sort_qids_by_fracpre_desc(dataframe=hist_item_data,
                                                    qids=[i for i in hist_item_data.index if 'a' in i])
    qids_expert = item_plot.sort_qids_by_fracpre_desc(dataframe=hist_item_data,
                                                    qids=[i for i in hist_item_data.index if 'b' in i])
    qids_grades = item_plot.sort_qids_by_fracpre_desc(dataframe=hist_grades,
                                                    qids=[i for i in hist_grades.index if 'c' in i], sortby='fracpost')
    #print(qids_grades)
    #print(hist_grades)

    """--------------------------
    historical data calculations
    """#-------------------------
    historical_N = max(historical_raw_data.count())
    historical_gender = historical_raw_data.groupby('Q54').Q54.size()/historical_raw_data.Q54.size
    
    hist_valcnt_Q50 = historical_raw_data['Q50'].value_counts()
    hist_n_Q50 = historical_raw_data['Q50'].size
    # hist_interestShift = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), hist_n_Q50) for val in hist_valcnt_Q50]))
    hist_interestShift = pd.DataFrame(np.array([(val/hist_n_Q50, 0) for val in hist_valcnt_Q50]))
    hist_interestShift.columns = ['Similar level classes', 'conf (similar)']

    hist_valcnt_Q49 = historical_raw_data['Q49'].value_counts()
    hist_valcnt_Q49 = utilities.ReplaceMissingRowsWithZeros(dataSeries=hist_valcnt_Q49, expectedRows=expectedRows_Q49)
    hist_n_Q49 = historical_raw_data['Q49'].size
    # hist_currentInterest = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), hist_n_Q49, n_LikertLevels=6) for val in hist_valcnt_Q49]))
    hist_currentInterest = pd.DataFrame(np.array([(val/hist_n_Q49, 0) for val in hist_valcnt_Q49]))
    hist_currentInterest.columns = ['Similar level classes', 'conf (similar)']
    
    hist_valcnt_47 = historical_raw_data['Q47'].value_counts()
    hist_valcnt_47 = utilities.ReplaceMissingRowsWithZeros(dataSeries=hist_valcnt_47, expectedRows=expectedRows_Q47)
    hist_n_Q47 = historical_raw_data['Q47'].size
    # hist_declaredMajor = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), hist_n_Q47, n_LikertLevels=6) for val in hist_valcnt_47]))
    hist_declaredMajor = pd.DataFrame(np.array([(val/hist_n_Q47, 0) for val in hist_valcnt_47]))
    hist_declaredMajor.columns = ['Similar level classes', 'conf (similar)']
 
    historical_futurePlans = utilities.futurePlansData(historical_raw_data)
    history_futureplans_df = pd.DataFrame({'Similar level classes':historical_futurePlans[:,0]}
                                , index=historical_futurePlans[:,1]).astype('float64')

    #print("Historical data loaded and calculated. . .")

    for course, ID_date in zip(courseIDs,courseIDs_Date):
        
        if timing == True:
            one_report_start = timeit.default_timer()

        # create dataframe of course data
        individual_course_raw_data = course_raw_data[course_raw_data.courseID == course]

        # calculate n-values for course data
        course_N = max(individual_course_raw_data.count())
        if course_N == 0:
            #raise NoCourseDataError("There was no data for course '{CourseName}'.".format(CourseName=course))
            print("There was no data for course '{CourseName}'.\nMoving to next course data. . .".format(CourseName=course))
            continue
            

        # create directories based on course IDS from course data and date
        if not os.path.exists(ID_date):
            course_dir = parent_dir + '\\' + ID_date
            #print(course_dir)
            os.makedirs(course_dir, exist_ok=True)
        else:
            course_dir = parent_dir + '\\' + ID_date
            #print(course_dir + ' : Already exists.')

        # create images directory
        course_img_dir = parent_dir+'\\' + ID_date + '\\Images'
        if not os.path.exists(course_img_dir):
            print(course_img_dir)
            os.makedirs(course_img_dir, exist_ok=True)
        else:
            print(course_img_dir + ' : Already exists.')

        image_save_directory = course_img_dir + '\\'

        print(image_save_directory)

        # copy stock images
        shutil.copy(parent_dir + '\\stock images\\' + 'Single_Question_2D_pre_post_Hist.png', image_save_directory)
        shutil.copy(parent_dir + '\\stock images\\' + 'Single_Question_Interleaved_pre_post_Hist.png', image_save_directory)
        shutil.copy(parent_dir + '\\stock images\\' + 'Single_Question_pre_post_change.png', image_save_directory)


        course_item_data = item_plot.make_eclass_item_dataframe(df=individual_course_raw_data)

        # plot 'What do YOU think?' question
        ####################################
        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='What do YOU think?')
        item_plot.plot_itemized_data(data=hist_item_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_WHAT, color='red')
        item_plot.plot_itemized_data(data=course_item_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids_WHAT, color='blue')    
        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory+'whatdoYOUThink.png', bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality
        fig.savefig(image_save_directory+'highquality_whatdoYOUThink.png', bbox_inches='tight')

        # plot 'What do EXPERTS think?' question
        ########################################
        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='What do experts think?')
        item_plot.plot_itemized_data(data=hist_item_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_expert, color='red')
        item_plot.plot_itemized_data(data=course_item_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids_expert, color='blue')    
        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory+'whatdoExpertsThink.png', bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality
        fig.savefig(image_save_directory+'highquality_whatdoExpertsThink.png', bbox_inches='tight')

        # plot 'grades' question
        ########################
        course_grades = utilities.expertLikeResponseDataFrame(rawdata_df=individual_course_raw_data
                                                         , columnIDs=Questions.post_GradeQuestionIDs
                                                         , CI_Calculator=utilities.confidenceInterval
                                                         , grades=True)
        course_grades.columns = ['cipost','fracpost']
        
        #print(course_grades.index)

        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='How important for earning a good grade in this class was...')
        item_plot.plot_itemized_data(data=hist_grades, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_grades, color='red', grades=True)
        item_plot.plot_itemized_data(data=course_grades, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids_grades, color='blue', grades=True)    
        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory+'grades.png', bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality
        fig.savefig(image_save_directory+'highquality_grades.png', bbox_inches='tight')        
        


        #print(hist_item_data.mean())
        #print(course_item_data.mean())

        #hist_agg = hist_item_data[qids_WHAT].mean().transpose()
        #course_agg = course_item_data[qids_WHAT].mean().transpose()

        #fracprepost = hist_agg[['fracpre', 'fracpost']].join(course_agg[['fracpre', 'fracpost']], lsuffix=' hist', rsuffix=' course')
        #errorprepost = hist_agg[['cipre', 'cipost']].join(course_agg[['cipre', 'cipost']], lsuffix=' hist', rsuffix=' course')
        

        # aggregate 'What do YOU think' question
        agg_df = hist_item_data.join(course_item_data, lsuffix=' hist', rsuffix=' course')
        #agg_df = agg_df.ix[[question[:-2] for question in Questions.pre_WhatDoYouThinkQuestionIDs]]
        agg_df = agg_df.ix[qids_WHAT]
        
        #print(agg_df)
        agg_df = agg_df.mean()



        #print(agg_df)

        #print(agg_df['cipre [1]'])

        #data = np.array([[agg_df[2], agg_df[6]]
        #                ,[agg_df[3], agg_df[7]]])
        #error = np.array([[agg_df[0], agg_df[1]]
        #                  , [agg_df[4], agg_df[5]]])

        #print(agg_df)

        data = np.array([[agg_df['fracpre hist'], agg_df['fracpre course']]
                         ,[agg_df['fracpost hist'], agg_df['fracpost course']]])
        error = np.array([[agg_df['cipre hist'], agg_df['cipre course']]
                          ,[agg_df['cipost hist'], agg_df['cipost course']]]).transpose()

        #print(data)
        #print(error)

        data = pd.DataFrame(data)
        data.index = ['pre', 'post']
        data.columns = ['Similar level courses', 'Your course']
        ax = data.plot(kind='bar', yerr=error, color=['blue', 'red'], alpha=0.75)
        ax.set_ylim(0,1)
        ax.legend(loc='lower left')
        ax.set_title('Overall E-CLASS Score on\n"What do YOU think..." statements\nN(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        ax.set_ylim(0,1)
        ax.legend(loc='lower left')
        ax.set_xticklabels(labels=['pre','post'], rotation=0)
        ax.set_ylabel('Fraction of statements\nwith expert-like responses')
        fig = ax.get_figure()

        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory+'overall.png', bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality
        fig.savefig(image_save_directory+'highquality_overall.png', bbox_inches='tight')

        del agg_df, data, error, fig, ax

        course_gender = individual_course_raw_data.groupby('Q54').Q54.size()/individual_course_raw_data.Q54.size

        gender_df = pd.DataFrame({'Similar level classes':historical_gender
                                 ,'Your class':course_gender})

        gender_df.index = ['Female', 'Male', 'Prefer not to say']

        ax = gender_df.plot(kind='bar', color=['blue', 'red']
                           , alpha=0.75)



        ax.set_title('What is your gender?')
        ax.set_ylim(0,1)
        ax.set_ylabel('Fraction of Students')
        ax.set_xticklabels(['Female', 'Male', 'Prefer not to say'], rotation=45)
        fig = ax.get_figure()
        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory + 'gender.png',bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality  
        fig.savefig(image_save_directory + 'highquality_gender.png',bbox_inches='tight')

        # plot futureplans.png
        # TODO : WTF is individual_course_DF
        course_futurePlans = utilities.futurePlansData(individual_course_raw_data)

        # this line should probably go into utilities.futurePlansData
        course_df = pd.DataFrame({'Your class':course_futurePlans[:,0]}
                                , index=course_futurePlans[:,1]).astype('float64')

        futurePlans_df = history_futureplans_df.join(course_df)

        ax = futurePlans_df.plot(kind='barh', color=['blue', 'red'], alpha=0.75)
        ax.set_title('Future Plans\nN(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        ax.set_xlim(0,1)
        ax.set_xlabel('Fraction of Students')
        fig = ax.get_figure()

        # TODO: function out the savefig function
        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory + 'futureplans.png',bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality 
        fig.savefig(image_save_directory + 'highquality_futureplans.png',bbox_inches='tight')

        # plot interestshift.png
        course_valcnt = individual_course_raw_data['Q50'].value_counts()
        course_n = individual_course_raw_data['Q50'].size
        
        # course_interestShift = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), course_n) for val in course_valcnt]))
        course_interestShift = pd.DataFrame(np.array([(val/course_n, 0) for val in course_valcnt]))
        course_interestShift.columns = ['Your class', 'conf (your)']

        df = hist_interestShift.join(course_interestShift)

        errors = df[['conf (similar)', 'conf (your)']].copy()
        errors.columns = ['Similar level classes', 'Your class']

        #ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75, yerr=errors)
        ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75)
        ax.set_ylim(0,1)
        ax.set_xticklabels(['Increased', 'Stayed the same', 'Decreased'], rotation=45)
        ax.set_ylabel('Fraction of Students')
        ax.set_title('During the semester, my interest in physics. . .\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        fig = ax.get_figure()

        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory + 'interestshift.png',bbox_inches='tight',dpi=DPI)
    
        # save fig with larger dpi for publication quality 
        fig.savefig(image_save_directory + 'highquality_interestshift.png',bbox_inches='tight')



        # plot currentinterest.png
        course_valcnt = individual_course_raw_data['Q49'].value_counts()
        course_valcnt = utilities.ReplaceMissingRowsWithZeros(dataSeries=course_valcnt, expectedRows=expectedRows_Q49)
        course_n = individual_course_raw_data['Q49'].size
        
        course_interestShift = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), course_n, n_LikertLevels=6) for val in course_valcnt]))
        course_interestShift.columns = ['Your class', 'conf (your)']

        df = hist_currentInterest.join(course_interestShift)

        errors = df[['conf (similar)', 'conf (your)']].copy()
        errors.columns = ['Similar level classes', 'Your class']

        # ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75, yerr=errors)
        ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75)
        ax.set_ylim(0,1)
        ax.set_xticklabels(['Very Low', 'Low', 'Moderate', 'High', 'Very High', 'N/A'], rotation=45)
        ax.set_ylabel('Fraction of Students')
        ax.set_title('Currrently, what is your interest in physics?\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        fig = ax.get_figure()

        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory + 'currentinterest.png',bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality 
        fig.savefig(image_save_directory + 'highquality_currentinterest.png',bbox_inches='tight')



        # plot declaredmajor.png
        course_valcnt = individual_course_raw_data['Q47'].value_counts()
        course_valcnt = utilities.ReplaceMissingRowsWithZeros(dataSeries=course_valcnt, expectedRows=expectedRows_Q47)
        course_n = individual_course_raw_data['Q47'].size

        # course_declaredMajor = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), course_n, n_LikertLevels=6) for val in course_valcnt]))
        course_declaredMajor = pd.DataFrame(np.array([(val/course_n,0) for val in course_valcnt]))
        course_declaredMajor.columns = ['Your class', 'conf (your)']

        df = hist_declaredMajor.join(course_declaredMajor)

        errors = df[['conf (similar)', 'conf (your)']].copy()
        errors.columns = ['Similar level classes', 'Your class']

        #ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75, yerr=errors)
        ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75)

        ax.set_ylim(0,1)
        ax.set_xticklabels([qstr for qstr in questionAnswers.values()], rotation=90)
        ax.set_ylabel('Fraction of Students')
        ax.set_title('What is your current major?\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        
        fig = ax.get_figure()

        # save fig  with smaller dpi for faster loading on browsers
        fig.savefig(image_save_directory + 'declaredmajor.png',bbox_inches='tight', dpi=DPI)
    
        # save fig with larger dpi for publication quality 
        fig.savefig(image_save_directory + 'highquality_declaredmajor.png',bbox_inches='tight')

        # copy the static pages into the course directory
        #for item in ['howtoread.html', 'analysis.html', 'questionlist.html']:
        #    shutil.copy2(item, course_dir)

        # generate the report.html
       # print(os.getcwd())
        TemplateLoader = jinja2.FileSystemLoader(searchpath="C:\\Users\\John\\Source\\Repos\\ECLASS-Report-Generator")
        TemplateEnv = jinja2.Environment(loader=TemplateLoader)
        Template = TemplateEnv.get_template('template.html')

        #for page in ['report.html', 'howtoread.html', 'analysis.html', 'questionlist.html']:
        for page in ['report', 'howtoread', 'analysis', 'questionlist']:

            RenderedTemplate = Template.render({'title': course_dir#'school name'
                            , 'link': [[course_dir+'//'+page+'.html' for page in ['report', 'howtoread', 'analysis', 'questionlist']]]*2
                            , 'email': "eclass@colorado.edu"
                            , 'table1': [['no'],['data']]
                            , 'low_N' : True if course_N < 10 else False
                            , 'questionlist': Questions.questionList()
                            , 'navbar': zip(["Report", "How to Read This Report", "How This Report was Analyzed", "Question List"]
                                              ,["report.html", "howtoread.html", "analysis.html", "questionlist.html"])
                            , 'page': page})
            with open(course_dir + '//' + page + '.html', 'wb+') as report:
                report.write(RenderedTemplate.encode())
                report.close()


        # delete dataframe of course data
        del course_df, futurePlans_df, gender_df, df
        plt.close('all')

        if timing == True:
            one_report_end = timeit.default_timer()
            print('Single report runtime: ', one_report_end - one_report_start)
    
    end = timeit.default_timer()
    print("Total run time: ", end - start)
