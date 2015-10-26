
# pylint: disable=C0321
# pylint: disable=C0303
# pylint: disable=line-too-long

import os
import glob
import pandas as pd
import hashlib
import Questions

q = Questions.Questions()

#questionIDs = ['q01a','q01b','q02a','q02b','q03a','q03b','q04a','q04b','q05a','q05b','q06a','q06b','q07a','q07b'
#               ,'q09a','q09b','q10a','q10b','q11a','q11b','q12a','q12b','q13a','q13b','q14a','q14b','q15a','q15b'
#               ,'q16a','q16b','q17a','q17b','q18a','q18b','q19a','q19b','q20a','q20b','q21a','q21b','q22a','q22b'
#               ,'q23a','q23b','q24a','q24b','q25a','q25b','q26a','q26b','q27a','q27b','q28a','q28b','q29a','q29b'
#               ,'q30a','q30b','q31a','q31b','q40a','q40b']


def BuildAggregateDataFrame(filenames, coursetype, name):
    """
    combines all data from csv's in a filename list
    into a single dataframe
    """
    df = pd.DataFrame()
    for filename in filenames:
        concat_df = pd.read_csv(filename)
        
        concat_df['courseID'] = filename.split(name)[0]
        concat_df['coursetype'] = coursetype
        concat_df.Q3_3_TEXT = concat_df.Q3_3_TEXT.astype(str)
        df = pd.concat([df, concat_df])
    return df

def DeleteResponsesToDiscardQuestion(dataframe):
    dataframe = dataframe[dataframe.q40a != 4]

def DeleteNotNeededColumns(df):
    """
    To keep time to completion data remove 'V8' and 'V9'
    from NotNeededColumns list
    """

    #NotNeededColumns = ['V2','V3','V4','V5','V6','V7','V8','V9','V10']
    NotNeededColumns = ['V2','V3','V4','V5','V6','V7','V8','V9','V10', 'q40a', 'q40b']
    for col in NotNeededColumns:
        del df[col]

def ShiftNegativeQuestions(dataframe):
    """ 
    converts numbers to negative numbers for specific question columns
    """
    #negativequestions = ['q02a'
    #                    ,'q02b'
    #                    ,'q03a'
    #                    ,'q03b'
    #                    ,'q07a'
    #                    ,'q07b'
    #                    ,'q09a'
    #                    ,'q09b'
    #                    ,'q14a'
    #                    ,'q14b'
    #                    ,'q16a'
    #                    ,'q16b'
    #                    ,'q17a'
    #                    ,'q17b'
    #                    ,'q24a'
    #                    ,'q24b'
    #                    ,'q29a'
    #                    ,'q29b'
    #                    ,'q30a'
    #                    ,'q30b']

    #for question in negativequestions:
    for question in q.negativequestions:
        dataframe[question] = dataframe[question] * -1 + 6

def DeleteNANIdentifiers(dataframe):
    
    firstname_lastname_studentID = ['Q3_1_TEXT', 'Q3_2_TEXT', 'Q3_3_TEXT']
    dataframe.dropna(subset=['Q3_1_TEXT', 'Q3_2_TEXT'], how='all', inplace=True)
    dataframe.dropna(subset=['Q3_2_TEXT', 'Q3_3_TEXT'], how='all', inplace=True)
    dataframe.dropna(subset=['Q3_1_TEXT', 'Q3_3_TEXT'], how='all', inplace=True)

def DeleteEmptyResponses(dataframe):
    """
    Deletes rows where no survey questions were answered.
    """
    dataframe.dropna(thresh=18, inplace=True)

def SaveDataFrameToCSV(dataframe, name):
    dataframe.to_csv(name+'Munged_Aggregate_Data.csv', index=False)

def strtoint(s):
    """
    Some institutions may have strings instead of numeric student IDs
    This function converts them into ints using the hashlib library
    built into the python standard library
    """
    return int(int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** 8))

def MergeQuestionResponses(df):
    """
    All questions should be merged from 1,2,3,4,5 to 1,3,5
    i.e. strongly agree and agree combine, strongly disagree
    and disagree combine, and neutral stays the same

    This method should be implemented before ShiftNegativeQuestions()
    """

    def merge(value):
        """
        5 = strongly agree
        4 = agree
        3 = neutral
        2 = disagree
        1 = strongly disagree
        """
        if value == 4:
            return 5
        elif value == 2:
            return 1
        elif value > 5 or value < 1:
            raise ValueError('responses should be between 1 and 5')
        else:
            return value


    for qst in q.questionIDs:
        df[qst] = df[qst].apply(merge)

def cleanDataPipeline(dir):
    """
    scrapes directory for pre and post survey files to create
    an aggregate cleaned csv of all course data.
    """
    
    os.chdir(dir)

    #name can be 'pre' or 'post'
    name = ['pre', 'post']
    for n in name:
        pre_filenames = glob.glob('*'+n+'.csv')

        raw_df = BuildAggregateDataFrame(pre_filenames, coursetype='LowerDivision', name=n)
        #post_df = BuildAggregateDataFrame(post_filenames, coursetype='UpperDivision')

        #delete responses that didn't answer the checker question
        DeleteResponsesToDiscardQuestion(raw_df) 
        #print(pre_df.head())

        #Delete Not Needed Columns
        DeleteNotNeededColumns(raw_df)

        #Merge Questions
        MergeQuestionResponses(raw_df)

        #shift negative asked questions to positive to align 
        ShiftNegativeQuestions(raw_df)
        #print(pre_df['q02a'].head())

        #Remove Rows with Null first names, last names, studentIDs
        DeleteNANIdentifiers(raw_df)
        #print(pre_df.head())

        #Delete empty responses
        DeleteEmptyResponses(raw_df)

        #convert IDs to ints (some IDs have strings)
        raw_df.Q3_3_TEXT = raw_df.Q3_3_TEXT.apply(strtoint)

        #write munged DataFrame to CSV
        SaveDataFrameToCSV(raw_df, n)


if __name__ == "__main__":

    cleanDataPipeline(dir='C:\\Users\\John\\Desktop\\upper vs lower\\intro_new')

