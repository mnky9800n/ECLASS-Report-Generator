
"""
[0] import Questions, UtilitiesForPlotting, DataCleaner, BuildReport

[1] load historical data

[2] load course data

[3] load faculty survey data

[4] use DataCleaner on course data

[5] create directories based on course IDs from course data

[6] for course in data:

        plot overall.png
        plot wdyt1.png
        plot wdyt2.png
        plot wdytvswdet1.png
        plot wdytvswdet2.png
        plot grade1.png
        plot grade2.png
        plot declaredmajor.png
        plot currentinterest.png
        plot gender.png
        plot futureplans.png

        create Table1

        use BuildReport to generate report
"""

import Questions
import UtilitiesForPlotting as utilities
import DataCleaner
import BuildReport
import os
import pandas as pd
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import shutil
import jinja2

class NoCourseDataError(Exception):
    pass

class NoArgsError(Exception):
    pass


def load_pre_post_data(pre, post):
    """
    loads cleaned data and returns a pandas dataframe
    of the merged data.
    """
    #print(pre)
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

def itemized_survey_plotting_pipeline(hist_df, course_df, question_block, qlen, title, image_save_directory, save_title):
    """
    Pipeline for plotting itemized survey question plots

    Parameters:
    ---------------------
    hist_data : pandas DataFrame
    """
    _questions = [question[:-2] for question in question_block]
    _questiontext = [q.questionIDToQuestionText[key] for key in _questions]
    _hist = utilities.sliceDataForItemizedPlot(df=hist_df, questionListForSlicing=_questions)
    _course = utilities.sliceDataForItemizedPlot(df=course_df, questionListForSlicing=_questions)
    fig, ax = utilities.createFigureForItemizedSurveyData(questions=_questiontext, legendLabels=['Similiar level courses', 'Your course']
                                       ,title=title)
    
    fig, ax = utilities.plotItemizedData(preData=_hist['pre']
                     ,postData=_hist['post']
                     ,confData=_hist['conf']
                     ,offset=0.2
                     ,fig=fig
                     ,ax=ax
                     ,color='blue')
    
    fig, ax = utilities.plotItemizedData(preData=_course['pre']
                             ,postData=_course['post']
                             ,confData=_course['conf']
                             ,offset=-0.2
                             ,fig=fig
                             ,ax=ax
                             ,color='red')
    fig.savefig(image_save_directory+save_title, bbox_inches='tight')#'\\WhatDoYouThink1.png')

if __name__ == "__main__":

    q = Questions.Questions()
    expectedRows_Q49 = [1.,2.,3.,4.,5.,6.]
    questionAnswers = {1.0: 'Physics', 2.0: 'Chemistry', 3.0: 'Biochemistry', 4.0: 'Biology', 5.0: 'Engineering', 6.0: 'Engineering Physics', 7.0: 'Astronomy', 8.0: 'Astrophysics', 9.0: 'Geology/geophysics', 10.0: 'Math/Applied Math', 11.0: 'Computer Science', 12.0: 'Physiology', 13.0: 'Other Science', 14.0: 'Non-science Major', 15.0: 'Open option/Undeclared'}
    expectedRows_Q47 = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,15.]

    main, pre_hist, post_hist, coursedir, instructordata = get_sys_args()

    historical_raw_data = load_pre_post_data(pre=pre_hist, post=post_hist)
    

    DataCleaner.cleanDataPipeline(coursedir)

    course_raw_data = load_pre_post_data(pre='preMunged_Aggregate_Data.csv'
                                   ,post='postMunged_Aggregate_Data.csv')

    # TODO: load faculty survey data

    # get all unique course ideas, append the current GMT year and month
    # to them
    courseIDs = list(set(course_raw_data.courseID.values))
    courseIDs_Date = [m for m in map(add_date, courseIDs)]

    parent_dir = os.getcwd()

    #  create expert like response data frame : pre history data
    pre_hist = utilities.expertLikeResponseDataFrame(rawdata_df=historical_raw_data
                                                    , columnIDs=q.pre_WhatDoYouThinkQuestionIDs+q.pre_ExperimentalPhysicistQuestionIDs
                                                    , CI_Calculator=utilities.confidenceInterval)
    #  create expert like response data frame : post history data
    post_hist = utilities.expertLikeResponseDataFrame(rawdata_df=historical_raw_data
                                                     , columnIDs=q.post_WhatDoYouThinkQuestionIDs+q.post_ExperimentalPhysicistQuestionIDs
                                                     , CI_Calculator=utilities.confidenceInterval)
    
    #  create expert like response data frame : grades history data
    grades_hist = utilities.expertLikeResponseDataFrame(rawdata_df=historical_raw_data
                                                       ,columnIDs=q.post_GradeQuestionIDs
                                                       ,grades=True
                                                       , CI_Calculator=utilities.confidenceInterval)
    
    #  create combined dataframe of all data pre/post/grades
    df = pre_hist.join(post_hist, lsuffix=' (pre)', rsuffix=' (post)')
    grades_hist.columns = ['Confidence Interval (post)', 'Fraction of Students with Expert Like Response (post)']
    hist_df = pd.concat([df, grades_hist])

    # historical data calculations
    historical_N = max(historical_raw_data.count())
    historical_gender = historical_raw_data.groupby('Q54').Q54.size()/historical_raw_data.Q54.size
    
    hist_valcnt_Q50 = historical_raw_data['Q50'].value_counts()
    hist_n_Q50 = historical_raw_data['Q50'].size
    # hist_interestShift = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), hist_n_Q50) for val in hist_valcnt_Q50]))
    hist_interestShift = pd.DataFrame(np.array([(0, hist_n_Q50) for val in hist_valcnt_Q50]))
    hist_interestShift.columns = ['Similar level classes', 'conf (similar)']

    hist_valcnt_Q49 = historical_raw_data['Q49'].value_counts()
    hist_valcnt_Q49 = utilities.ReplaceMissingRowsWithZeros(dataSeries=hist_valcnt_Q49, expectedRows=expectedRows_Q49)
    hist_n_Q49 = historical_raw_data['Q49'].size
    # hist_currentInterest = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), hist_n_Q49, n_LikertLevels=6) for val in hist_valcnt_Q49]))
    hist_currentInterest = pd.DataFrame(np.array([(0, hist_n_Q49) for val in hist_valcnt_Q49]))
    hist_currentInterest.columns = ['Similar level classes', 'conf (similar)']
    
    hist_valcnt_47 = historical_raw_data['Q47'].value_counts()
    hist_valcnt_47 = utilities.ReplaceMissingRowsWithZeros(dataSeries=hist_valcnt_47, expectedRows=expectedRows_Q47)
    hist_n_Q47 = historical_raw_data['Q47'].size
    # hist_declaredMajor = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), hist_n_Q47, n_LikertLevels=6) for val in hist_valcnt_47]))
    hist_declaredMajor = pd.DataFrame(np.array([(0, hist_n_Q47) for val in hist_valcnt_47]))
    hist_declaredMajor.columns = ['Similar level classes', 'conf (similar)']
 
    historical_futurePlans = utilities.futurePlansData(historical_raw_data)
    history_futureplans_df = pd.DataFrame({'Similar level classes':historical_futurePlans[:,0]}
                                , index=historical_futurePlans[:,1]).astype('float64')

    for course, ID_date in zip(courseIDs,courseIDs_Date):

        # create dataframe of course data
        individual_course_DF = course_raw_data[course_raw_data.courseID == course]

        # calculate n-values for course data
     
        course_N = max(individual_course_DF.count())
        if course_N == 0:
            raise NoCourseDataError("There was no data for course '{CourseName}'.".format(CourseName=course))
            break

        # create expert like response data frame : pre course data
        pre_course = utilities.expertLikeResponseDataFrame(rawdata_df=individual_course_DF
                                                           , columnIDs=q.pre_WhatDoYouThinkQuestionIDs+q.pre_ExperimentalPhysicistQuestionIDs
                                                           , CI_Calculator=utilities.confidenceInterval)

        # create expert like response data frame : post course data
        post_course = utilities.expertLikeResponseDataFrame(rawdata_df=individual_course_DF
                                                            , columnIDs=q.post_WhatDoYouThinkQuestionIDs+q.post_ExperimentalPhysicistQuestionIDs
                                                            , CI_Calculator=utilities.confidenceInterval)

        # create expert like response data frame : grades course data
        grades_course = utilities.expertLikeResponseDataFrame(rawdata_df=individual_course_DF
                                                              , columnIDs=q.post_GradeQuestionIDs
                                                              , CI_Calculator=utilities.confidenceInterval
                                                              , grades=True)
        
        # create combined dataframe for all course_data
        df = pre_course.join(post_course, lsuffix=' (pre)', rsuffix=' (post)')
        grades_course.columns = ['Confidence Interval (post)', 'Fraction of Students with Expert Like Response (post)']
        course_df = pd.concat([df, grades_course])

        # create directories based on course IDS from course data and date
        if not os.path.exists(ID_date):
            course_dir = parent_dir+ '\\' + ID_date
            print(course_dir)
            os.makedirs(course_dir, exist_ok=True)

        # create images directory
        course_img_dir = parent_dir+'\\' + ID_date + '\\images'
        if not os.path.exists(course_img_dir):
            print(course_img_dir)
            os.makedirs(course_img_dir, exist_ok=True)

        image_save_directory = course_img_dir + '\\'

        # plot overall.png
        agg_df = hist_df.join(course_df, lsuffix=' [1]', rsuffix=' [2]')
        agg_df = agg_df.ix[[question[:-2] for question in q.pre_WhatDoYouThinkQuestionIDs]]
        agg_df = agg_df.mean()

        data = np.array([[agg_df[2], agg_df[6]]
                        ,[agg_df[3], agg_df[7]]])
        error = np.array([[agg_df[0], agg_df[1]]
                          , [agg_df[4], agg_df[5]]])

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
        fig.savefig(image_save_directory+'overall.png', bbox_inches='tight')
        del agg_df, data, error, fig, ax

        # plot whatdoyouthink1.png
        qlen = len(q.pre_WhatDoYouThinkQuestionIDs)
        itemized_survey_plotting_pipeline(hist_df=hist_df
                                       , course_df=course_df
                                       , qlen=qlen
                                       , question_block=q.pre_WhatDoYouThinkQuestionIDs[:int(qlen/2)]
                                       , title='What do YOU think? (part 1)'
                                       , image_save_directory=image_save_directory
                                       , save_title='whatdoyouthink1.png')

        # plot whatdoyouthink2.png
        itemized_survey_plotting_pipeline(hist_df=hist_df
                                       , course_df=course_df
                                       , qlen=qlen
                                       , question_block=q.pre_WhatDoYouThinkQuestionIDs[int(qlen/2):]
                                       , title='What do YOU think? (part 2)'
                                       , image_save_directory=image_save_directory
                                       , save_title='whatdoyouthink2.png')

        # plot expertvsyou1.png
        qlen = len(q.pre_ExperimentalPhysicistQuestionIDs)
        itemized_survey_plotting_pipeline(hist_df=hist_df
                                       , course_df=course_df
                                       , question_block=q.pre_ExperimentalPhysicistQuestionIDs[int(qlen/2):]
                                       , title='What do YOU think? and \nWhat would experimental physicists say \nabout their research? (part 1)'
                                       , image_save_directory=image_save_directory
                                       , save_title='expertvsyou1.png'
                                       , qlen=qlen)

        # plot expertvsyou2.png
        itemized_survey_plotting_pipeline(hist_df=hist_df
                                       , course_df=course_df
                                       , question_block=q.pre_ExperimentalPhysicistQuestionIDs[:int(qlen/2)]
                                       , title='What do YOU think? and \nWhat would experimental physicists say \nabout their research? (part 2)'
                                       , image_save_directory=image_save_directory
                                       , save_title='expertvsyou2.png'
                                       , qlen=qlen)
        
        # plot grades1.png
        qlen = len(q.post_GradeQuestionIDs)
        questions_plot1 = [question for question in q.post_GradeQuestionIDs[:int(qlen/2)]]
        questions_plot2 = [question for question in q.post_GradeQuestionIDs[int(qlen/2):]]
        question_text_plot1 = [q.questionIDToQuestionText[key] for key in questions_plot1]
        question_text_plot2 = [q.questionIDToQuestionText[key] for key in questions_plot2]

        fig, ax = utilities.createFigureForItemizedSurveyData(questions=question_text_plot1
                                                              , legendLabels=['Similar level courses'
                                                                              , 'Your course']
                                                              , title='How important for earning a good grade in this class was... (part 1)')

        fig, ax = utilities.plotGradeData(data=hist_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                       ,confData=hist_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                       ,offset=0.2
                       ,fig=fig
                       ,ax=ax
                       ,color='blue')
        fig, ax = utilities.plotGradeData(data=course_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                       ,confData=course_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                       ,offset=-0.2
                       ,fig=fig
                       ,ax=ax
                       ,color='red')
        fig.savefig(image_save_directory + 'grades1.png', bbox_inches='tight')

        # plot grades2.png
        fig, ax = utilities.createFigureForItemizedSurveyData(questions=question_text_plot2, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='How important for earning a good grade in this class was... (part 2)')


        fig, ax = utilities.plotGradeData(data=hist_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                               ,confData=hist_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                               ,offset=0.2
                               ,fig=fig
                               ,ax=ax
                               ,color='blue')

        fig, ax = utilities.plotGradeData(data=course_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                               ,confData=course_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                               ,offset=-0.2
                               ,fig=fig
                               ,ax=ax
                               ,color='red')
        fig.savefig(image_save_directory + 'grades2.png', bbox_inches='tight')

        # plot gender.png
        course_gender = individual_course_DF.groupby('Q54').Q54.size()/individual_course_DF.Q54.size

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
        fig.savefig(image_save_directory + 'gender.png',bbox_inches='tight')

        # plot futureplans.png
        course_futurePlans = utilities.futurePlansData(individual_course_DF)

        course_df = pd.DataFrame({'Your class':course_futurePlans[:,0]}
                                , index=course_futurePlans[:,1]).astype('float64')

        futurePlans_df = history_futureplans_df.join(course_df)

        ax = futurePlans_df.plot(kind='barh', color=['blue', 'red'], alpha=0.75)
        ax.set_title('Future Plans\nN(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        ax.set_xlim(0,1)
        ax.set_xlabel('Fraction of Students')
        fig = ax.get_figure()
        fig.savefig(image_save_directory + 'futureplans.png',bbox_inches='tight')

        # plot interestshift.png
        course_valcnt = individual_course_DF['Q50'].value_counts()
        course_n = individual_course_DF['Q50'].size
        
        # TODO : replace confidence interval calculator with (0,course_n)
        # TODO : replacel confidence intervaal calculator with (0, hist_n)
        # course_interestShift = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), course_n) for val in course_valcnt]))
        course_interestShift = pd.DataFrame(np.array([( 0, course_n) for val in course_valcnt]))
        course_interestShift.columns = ['Your class', 'conf (your)']

        df = hist_interestShift.join(course_interestShift)

        errors = df[['conf (similar)', 'conf (your)']].copy()
        errors.columns = ['Similar level classes', 'Your class']

        ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75
                    , yerr=errors)
        ax.set_ylim(0,1)
        ax.set_xticklabels(['Increased', 'Stayed the same', 'Decreased'], rotation=45)
        ax.set_ylabel('Fraction of Students')
        ax.set_title('During the semester, my interest in physics. . .\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        fig = ax.get_figure()
        fig.savefig(image_save_directory + 'interestshift.png',bbox_inches='tight')

        # plot currentinterest.png
        course_valcnt = individual_course_DF['Q49'].value_counts()
        course_valcnt = utilities.ReplaceMissingRowsWithZeros(dataSeries=course_valcnt, expectedRows=expectedRows_Q49)
        course_n = individual_course_DF['Q49'].size
        
        # TODO : replace confidence interval calculator with (0,course_n)
        # TODO : replacel confidence intervaal calculator with (0, hist_n)
        # course_interestShift = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), course_n, n_LikertLevels=6) for val in course_valcnt]))
        course_interestShift = pd.DataFrame(np.array([(0, course_n) for val in course_valcnt]))
        course_interestShift.columns = ['Your class', 'conf (your)']

        df = hist_currentInterest.join(course_interestShift)

        errors = df[['conf (similar)', 'conf (your)']].copy()
        errors.columns = ['Similar level classes', 'Your class']

        ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75
                    , yerr=errors)
        ax.set_ylim(0,1)
        ax.set_xticklabels(['Very Low', 'Low', 'Moderate', 'High', 'Very High', 'N/A'], rotation=45)
        ax.set_ylabel('Fraction of Students')
        ax.set_title('Currrently, what is your interest in physics?\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        fig = ax.get_figure()
        fig.savefig(image_save_directory + 'currentinterest.png',bbox_inches='tight')

        # plot declaredmajor.png
        course_valcnt = individual_course_DF['Q47'].value_counts()
        course_valcnt = utilities.ReplaceMissingRowsWithZeros(dataSeries=course_valcnt, expectedRows=expectedRows_Q47)
        course_n = individual_course_DF['Q47'].size

        # TODO : replace confidence interval calculator with (0,course_n)
        # TODO : replacel confidence intervaal calculator with (0, hist_n)
        # course_declaredMajor = pd.DataFrame(np.array([utilities.confidenceInterval(int(val), course_n, n_LikertLevels=6) for val in course_valcnt]))
        course_declaredMajor = pd.DataFrame(np.array([(0, course_n) for val in course_valcnt]))
        course_declaredMajor.columns = ['Your class', 'conf (your)']

        df = hist_declaredMajor.join(course_declaredMajor)

        errors = df[['conf (similar)', 'conf (your)']].copy()
        errors.columns = ['Similar level classes', 'Your class']

        ax = df.plot(kind='bar', y=['Similar level classes', 'Your class']
                     , color=['blue', 'red'], alpha=0.75, yerr=errors)
        ax.set_ylim(0,1)
        ax.set_xticklabels([qstr for qstr in questionAnswers.values()], rotation=90)
        ax.set_ylabel('Fraction of Students')
        ax.set_title('What is your current major?\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
        fig = ax.get_figure()
        fig.savefig(image_save_directory + 'declaredmajor.png',bbox_inches='tight')
        
        # TODO: create Report.html

        # copy the static pages into the course directory
        for item in ['howtoread.html', 'analysis.html', 'questionlist.html']:
            shutil.copy2(item, course_dir)

        # generate the report.html
        TemplateLoader = jinja2.FileSystemLoader(searchpath=os.getcwd())
        TemplateEnv = jinja2.Environment(loader=TemplateLoader)
        Template = TemplateEnv.get_template('template.html')
        RenderedTemplate = Template.render({'title': 'school name'
                        , 'link': [[course_dir+'//'+page+'.html' for page in ['report', 'howtoread', 'analysis', 'questionlist']]]*2
                        , 'email': "Bethany.Wilcox@colorado.edu"
                        , 'table1': [['no'],['data']]
                        , 'questionlist': q.questionIDToQuestionText
                        , 'navbar': zip(["Report", "How to Read This Report", "How This Report was Analyzed", "Question List"]
                                          ,["report.html", "howtoread.html", "analysis.html", "questionlist.html"])
                        , 'page': 'report'})
        with open(course_dir + '//report.html', 'wb+') as report:
            report.write(RenderedTemplate.encode())
            report.close()
        
        # delete dataframe of course data
        del course_df, futurePlans_df, gender_df, df, 
        plt.close('all')