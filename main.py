

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

    if len(args) == 4:
        return args
    else:
        raise ValueError("""
        You must provide 5 data source files
        as CSVs in the following order:

        pre-historical data
        post-historical data
        course data directory
        instructor survey data

        You have provided {length} arguments instead.
        """.format(length=len(args)))

def get_GMT_year_month():
    """
    returns GMT year and month as a string
    """
    t = time.gmtime()
    return str(t.tm_year) + '_' + str(t.tm_mon)

def add_date(id):
    return id + '_' + get_GMT_year_month()

# TODO: create table 1 function

# TODO: create plotting pipeline


if __name__ == "__main__":

    q = Questions.Questions()

    pre_hist, post_hist, coursedir, instructordata = get_sys_args()

    historical_df = load_pre_post_data(pre=pre_hist, post=post_hist)

    DataCleaner.cleanDataPipeline(coursedir)

    course_df = load_pre_post_data(pre='preMunged_Aggregate_Data.csv'
                                   ,post='postMunged_Aggregate_Data.csv')

    # TODO: load faculty survey data

    historical_N = max(historical_data.count())

    # get all unique course ideas, append the current GMT year and month
    # to them
    courseIDs = list(set(course_df.courseID.values))
    courseIDs_Date = [m for m in map(add_date, courseIDs)]

    # TODO: create directories based on course IDS from course data and date
    for course in courseIDs_Date:

        if not os.path.exists(course):
            os.makedir(course)

    parent_dir = os.getcwd()

    # TODO: create expert like response data frame : pre history data
    pre_hist = utilities.expertLikeResponseDataFrame(rawdata_df=historical_df
                                                    , columnIDs=q.pre_WhatDoYouThinkQuestionIDs+q.pre_ExperimentalPhysicistQuestionIDs
                                                    , CI_Calculator=utilities.confidenceInterval)
    # TODO: create expert like response data frame : post history data
    post_hist = utilities.expertLikeResponseDataFrame(rawdata_df=historical_df
                                                     , columnIDs=q.post_WhatDoYouThinkQuestionIDs+q.post_ExperimentalPhysicistQuestionIDs
                                                     , CI_Calculator=utilities.confidenceInterval)
    
    # TODO: create expert like response data frame : grades history data
    grades_hist = utilities.expertLikeResponseDataFrame(rawdata_df=historical_df
                                                       ,columnIDs=q.post_GradeQuestionIDs
                                                       ,grades=True)
    
    # TODO: create combined dataframe of all data pre/post/grades
    hist_df = pd.concat([df, grades_hist])

    # TODO: create forloop for plotting, table and BuildReport
    for course, course_date in zip(courseIDs,courseIDs_Date):

        # TODO: create dataframe of course data
        individual_course_DF = course_df[course_df.courseID == course]

        # TODO: change working directory to course directory
        os.chdir(parent_dir + '//' + course_date)

        # TODO: create images directory
        if not os.path.exists('images'):
            os.makedirs('images')

        # TODO: calculate n-values for course data
        course_N = max(course_df.count())


        # TODO: create expert like response data frame : pre course data
        pre_course = utilities.expertLikeResponseDataFrame(rawdata_df=individual_course_DF
                                                           , columnIDs=q.pre_WhatDoYouThinkQuestionIDs+q.pre_ExperimentalPhysicistQuestionIDs
                                                           , CI_Calculator=utilities.confidenceInterval)

        # TODO: create expert like response data frame : post course data
        # TODO: create expert like response data frame : grades course data

        # TODO: plot overall.png
        # TODO: plot whatdoyouthink1.png
        # TODO: plot whadoyouthink2.png
        # TODO: plot expertvsyou1.png
        # TODO: plot expertvsyou2.png
        # TODO: plot grades1.png
        # TODO: plot grades2.png
        # TODO: plot gender.png
        # TODO: plot futureplans.png
        # TODO: plot shiftphysicsinterest.png
        # TODO: plot currentinterest.png
        # TODO: plot declaredmajor.png
        
        # TODO: create Report.html
        # TODO: return to parent directory
        os.chdir(parent_dir)

        # TODO: delete dataframe of course data

        # TODO: delete everything you've created so far

    pass
