

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

# TODO: import Questions, UtilitiesFor Plotting, DataClearner, BuildReport, os
import Questions
import UtilitiesForPlotting as utilities
import DataCleaner
import BuildReport
import os
import pandas as pd
import sys

# TODO: create function to load historical data
def load_historical_data(pre, post):
    """
    loads precleaned historical data for comparison to
    course data
    """
    predata = pd.read_csv(pre)#'preMunged_Aggregate_Data.csv')
    postdata = pd.read_csv(post)#'postMunged_Aggregate_Data.csv')

    return predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])

# TODO: gather sys args
def get_sys_args():
    args = [arg for arg in sys.argv]
    if len(args) != 5:
        raise ValueError("""
                         You must provide 5 data source files
                         as CSVs in the following order:
                         pre-historical data
                         post-historical data
                         pre-course data
                         post-course data
                         instructor survey data

                         You have provided {length} data source files.
                         """.format(length=len(args))
    else:
        return args

# TODO: create table 1 function

# TODO: create plotting pipeline

if __name__ == "__main__":

    # TODO: get sys args
    prehist, posthist,

    # TODO: load historical data

    # TODO: load course data

    # TODO: load faculty survey data

    # TODO: use DataCleaner on course data

    # TODO: calculate n-values for historical data
    
    # TODO: create directories based on course IDS from course data

    # TODO: create forloop for plotting, table and BuildReport

        # TODO: calculate n-values for course data
        # TODO: create expert like response data frame : pre history data
        # TODO: create expert like response data frame : post history data
        # TODO: create expert like response data frame : conf history data
        # TODO: create expert like response data frame : pre course data
        # TODO: create expert like response data frame : post course data
        # TODO: create expert like response data frame : conf course data

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

    pass
