r'C:/Users/John/Source/Repos/ECLASS-Report-Generator/data/historical_data/preMunged_Aggregate_Data.csv C:\Users\John\Source\Repos\ECLASS-Report-Generator\data\historical_data\postMunged_Aggregate_Data.csv C:\Users\John\Source\Repos\ECLASS-Report-Generator\data nothing'

r'C:\Users\John\Source\Repos\ECLASS-Report-Generator\data\intro_new\preMunged_Aggregate_Data.csv C:\Users\John\Source\Repos\ECLASS-Report-Generator\data\intro_new\postMunged_Aggregate_Data.csv C:\Users\John\Source\Repos\ECLASS-Report-Generator\data\intro_new\ nothing'
import Questions
import UtilitiesForPlotting as utilities
import DataCleaner
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
import table_one

class NoCourseDataError(Exception):
    pass

class ArgsError(Exception):
    pass

class TooManyArgsError(Exception):
    pass

class OldAggregateFilesExistError(Exception):
    pass


def get_sys_args():
    """
    checks for correct number of sys args present
    in command line string. Returns error if missing
    data.
    """
    args = [arg for arg in sys.argv]

    if len(args) == 6:#4: apparently main.py is an argument too. didn't know that.
        return args
    else:
        raise ArgsError("""
        You must provide 4 data source file locations and 1 target directory for reports
        as CSVs in the following order:

        1. pre-historical data
        2. post-historical data
        3. course data directory
        4. instructor survey data
        5. report target directory

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
    try:
        return id + '_' + get_GMT_year_month()
    except TypeError:
        raise OldAggregateFilesExistError('You need to delete the pre/post Aggregate files that were generated.')

if __name__ == "__main__":

    timing = True
    show_figs = True

    if timing == True:
        start = timeit.default_timer()

    # object instantiation (not neccessary)
    Questions = Questions.Questions()



    # plotting parameters
    svg = False
    DPI = 60
    expectedRows_Q49 = [1.,2.,3.,4.,5.,6.]
    questionAnswers = {1.0: 'Physics', 2.0: 'Chemistry', 3.0: 'Biochemistry', 4.0: 'Biology', 5.0: 'Engineering', 6.0: 'Engineering Physics', 7.0: 'Astronomy', 8.0: 'Astrophysics', 9.0: 'Geology/geophysics', 10.0: 'Math/Applied Math', 11.0: 'Computer Science', 12.0: 'Physiology', 13.0: 'Other Science', 14.0: 'Non-science Major', 15.0: 'Open option/Undeclared'}
    expectedRows_Q47 = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,15.]

    main, pre_hist, post_hist, coursedir, instructordata, report_target_directory = get_sys_args()
    

    # directory parameters
    #parent_dir = os.getcwd() + '\\data'
    parent_dir = report_target_directory

    # clean all data from current semester and prepare for plotting
    DataCleaner.cleanDataPipeline(coursedir)

    # load raw data into dataframes
    #course_raw_data, pre_responses, post_responses = utilities.load_pre_post_data(pre='preMunged_Aggregate_Data.csv',post='postMunged_Aggregate_Data.csv', course=True)
    course_raw_data, pre_responses, post_responses = utilities.load_pre_post_data(pre='PREMunged_Aggregate_Data.csv',post='POSTMunged_Aggregate_Data.csv', course=True)

    course_matched_count = course_raw_data.groupby('courseID').Q3_3_TEXT.count()

    historical_raw_data = utilities.load_pre_post_data(pre=pre_hist, post=post_hist, course=False)

    master_file = pd.read_csv(instructordata, skiprows=1)
    master_file['PreSurveyID'] = master_file['PreSurveyID'].apply(lambda x: x[3:])
    # get all unique course ideas, append the current GMT year and month
    courseIDs = list(set(course_raw_data.courseID.values))

    ##print(course_raw_data)
    #print(courseIDs)
    #import sys
    #sys.exit()

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

    for course, ID_date in zip(courseIDs,courseIDs_Date):
        
        if timing == True:
            one_report_start = timeit.default_timer()

        # create dataframe of course data
        individual_course_raw_data = course_raw_data[course_raw_data.courseID == course]

        #print(individual_course_raw_data[['survey_id_x','survey_id_y']].head())

        #print(master_file.columns)
        #print(master_file['PreSurveyID'].apply(lambda x: x[3:]))
        #print(individual_course_raw_data['survey_id_x'])
        #print(master_file[ master_file['PreSurveyID']==individual_course_raw_data['survey_id_x'].head(1)[0][3:]])
        #print(master_file[master_file['PreSurveyID']==individual_course_raw_data['survey_id_x'].iloc[0]]['Number of Students in Course'].iloc[0])
        reported_count = master_file[master_file['PreSurveyID']==individual_course_raw_data['survey_id_x'].iloc[0]]['Number of Students in Course'].iloc[0]
        # calculate n-values for course data
        course_N = max(individual_course_raw_data.count())


       
           
        #print(pre_responses['survey_id'])

        #print(course_raw_data[course_raw_data.courseID==course]['survey_id'])
        # table 1
        precount, postcount, matchedcount = table_one.get_counts_from_raw_data(pre=pre_responses, post=post_responses, matched=course_matched_count, course_id=course)

        #print(course)
        #print(course_raw_data.head())

        #reported_count = 5000
        #reported_count = table_one.get_reported_student_count()
        #reported_count = table_one.get_reported_student_count(df=master_file, course_id=course)

        #fraction_participating = table_one.fraction_of_participating_students(matched_count=matchedcount, reported_count=reported_count)
        fraction_participating = table_one.fraction_of_participating_students(matched_count=matchedcount, reported_count=reported_count)




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
        stock_image_dir = 'C:\\Users\\eclass\\Desktop\\ECLASS\\report generatory\\stock images\\'
        #shutil.copy(parent_dir + '\\stock images\\' + 'Single_Question_2D_pre_post_Hist.png', image_save_directory)
        #shutil.copy(parent_dir + '\\stock images\\' + 'Single_Question_Interleaved_pre_post_Hist.png', image_save_directory)
        #shutil.copy(parent_dir + '\\stock images\\' + 'Single_Question_pre_post_change.png', image_save_directory)
        shutil.copy(stock_image_dir + 'Single_Question_2D_pre_post_Hist.png', image_save_directory)
        shutil.copy(stock_image_dir + 'Single_Question_Interleaved_pre_post_Hist.png', image_save_directory)
        shutil.copy(stock_image_dir + 'Single_Question_pre_post_change.png', image_save_directory)


        course_item_data = item_plot.make_eclass_item_dataframe(df=individual_course_raw_data)
        

        # plot 'What do YOU think?' question
        ####################################
        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='What do YOU think?')
        item_plot.plot_itemized_data(data=hist_item_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_WHAT, color='black')
        item_plot.plot_itemized_data(data=course_item_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids_WHAT, color='red')
        item_plot.make_legend(ax=ax1, legend_labels=['Your Course', 'Similar Courses'], colors=['red','black'])
        utilities.save_fig(fig=fig, save_name=image_save_directory+'whatdoYOUThink', svg=svg)

        # plot 'What do EXPERTS think?' question
        ########################################
        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='What do experts think?')
        item_plot.plot_itemized_data(data=hist_item_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_expert, color='black')
        item_plot.plot_itemized_data(data=course_item_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids_expert, color='blue')
        item_plot.make_legend(ax=ax1, legend_labels=['Your Course', 'Similar Courses'], colors=['blue','black'])
        utilities.save_fig(fig=fig, save_name=image_save_directory+'whatdoExpertsThink', svg=svg)

        # plot 'What do EXPERTS think?' vs 'What do YOU think?' question
        ################################################################
        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='What do experts think? vs What do YOU think?')
        item_plot.plot_itemized_data(data=course_item_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_expert, color='blue')
        item_plot.plot_itemized_data(data=course_item_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=[q[0:3]+'a' for q in qids_expert], color='red')
        item_plot.make_legend(ax=ax1, legend_labels=['What do experts think?', 'What do YOU think?'], colors=['blue','red'])
        utilities.save_fig(fig=fig, save_name=image_save_directory+'versus', svg=svg)

        # plot 'grades' question
        ########################
        course_grades = utilities.expertLikeResponseDataFrame(rawdata_df=individual_course_raw_data
                                                         , columnIDs=Questions.post_GradeQuestionIDs
                                                         , CI_Calculator=utilities.confidenceInterval
                                                         , grades=True)
        course_grades.columns = ['cipost','fracpost']
        
        fig, ax1, ax2 = item_plot.make_itemized_single_figure(title='How important for earning a good grade in this class was...')
        item_plot.plot_itemized_data(data=hist_grades, offset=0.2, ax1=ax1, ax2=ax2, qids=qids_grades, color='black', grades=True)
        item_plot.plot_itemized_data(data=course_grades, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids_grades, color='yellow', grades=True)
        item_plot.make_legend(ax=ax1, legend_labels=['Your Course', 'Similar Courses'], colors=['yellow','black'])
        utilities.save_fig(fig=fig, save_name=image_save_directory+'grades', svg=svg)

        # aggregate 'What do YOU think' question
        agg_df = hist_item_data.join(course_item_data, lsuffix=' hist', rsuffix=' course')
        agg_df = agg_df.ix[qids_WHAT]
        
        agg_df = agg_df.mean()

        data = np.array([[agg_df['fracpre hist'], agg_df['fracpre course']]
                         ,[agg_df['fracpost hist'], agg_df['fracpost course']]])
        error = np.array([[agg_df['cipre hist'], agg_df['cipre course']]
                          ,[agg_df['cipost hist'], agg_df['cipost course']]]).transpose()
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

        utilities.save_fig(fig=ax.get_figure(), save_name=image_save_directory+'overall',svg=svg)
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
        utilities.save_fig(fig=ax.get_figure(), save_name=image_save_directory+'gender', svg=svg)
        
        course_futurePlans = utilities.futurePlansData(individual_course_raw_data)

        # this line should probably go into utilities.futurePlansData
        course_df = pd.DataFrame({'Your class':course_futurePlans[:,0]}
                                , index=course_futurePlans[:,1]).astype('float64')

        futurePlans_df = history_futureplans_df.join(course_df)

        ax = futurePlans_df.plot(kind='barh', color=['blue', 'red'], alpha=0.75)
        ax.set_title('Future Plans\nN(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        ax.set_xlim(0,1)
        ax.set_xlabel('Fraction of Students')
        utilities.save_fig(fig=ax.get_figure(), save_name=image_save_directory+'futureplans', svg=svg)

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
        utilities.save_fig(fig=ax.get_figure(), save_name=image_save_directory+'interestshift', svg=svg)

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
        utilities.save_fig(fig=ax.get_figure(), save_name=image_save_directory+'currentinterest', svg=svg)

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
        utilities.save_fig(fig=ax.get_figure(), save_name=image_save_directory+'declaredmajor', svg=svg)

        # generate the report.html
        # TODO : change template location for deployment
        #TemplateLoader = jinja2.FileSystemLoader(searchpath="C:\\Users\\John\\Source\\Repos\\ECLASS-Report-Generator")
        TemplateLoader = jinja2.FileSystemLoader(searchpath="C:\\Users\\eclass\\Source\\Repos\\ECLASS-Report-Generator")
        TemplateEnv = jinja2.Environment(loader=TemplateLoader)
        Template = TemplateEnv.get_template('template.html')

        for page in ['report', 'howtoread', 'analysis', 'questionlist']:
            # TODO : generate better title
            RenderedTemplate = Template.render({'title': course_dir
                            , 'link': [[course_dir+'//'+page+'.html' for page in ['report', 'howtoread', 'analysis', 'questionlist']]]*2
                            , 'email': "eclass@colorado.edu"
                            , 'table1': table_one.table_one_data(valid_pre=precount, valid_post=postcount, valid_matched=matchedcount, reported_student_count=reported_count, participating_student_fraction=fraction_participating)
                            , 'low_N' : True if course_N < 10 else False
                            , 'questionlist': Questions.questionList()
                            , 'navbar': zip(["Report", "How to Read This Report", "How This Report was Analyzed", "Question List"]
                                              ,["report.html", "howtoread.html", "analysis.html", "questionlist.html"])
                            , 'page': page
                            , 'svg' : svg})
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
