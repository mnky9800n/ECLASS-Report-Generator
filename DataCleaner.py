
# pylint: disable=C0321
# pylint: disable=C0303
# pylint: disable=line-too-long

import os
import glob
import pandas as pd
import hashlib

questionIDs = ['q01a','q01b','q02a','q02b','q03a','q03b','q04a','q04b','q05a','q05b','q06a','q06b','q07a','q07b'
               ,'q09a','q09b','q10a','q10b','q11a','q11b','q12a','q12b','q13a','q13b','q14a','q14b','q15a','q15b'
               ,'q16a','q16b','q17a','q17b','q18a','q18b','q19a','q19b','q20a','q20b','q21a','q21b','q22a','q22b'
               ,'q23a','q23b','q24a','q24b','q25a','q25b','q26a','q26b','q27a','q27b','q28a','q28b','q29a','q29b'
               ,'q30a','q30b','q31a','q31b','q40a','q40b']


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

    NotNeededColumns = ['V2','V3','V4','V5','V6','V7','V8','V9','V10']
    for col in NotNeededColumns:
        del df[col]

def ShiftNegativeQuestions(dataframe):
    """ 
    converts numbers to negative numbers for specific question columns
    """
    negativequestions = ['q02a'
                        ,'q02b'
                        ,'q03a'
                        ,'q03b'
                        ,'q07a'
                        ,'q07b'
                        ,'q09a'
                        ,'q09b'
                        ,'q14a'
                        ,'q14b'
                        ,'q16a'
                        ,'q16b'
                        ,'q17a'
                        ,'q17b'
                        ,'q24a'
                        ,'q24b'
                        ,'q29a'
                        ,'q29b'
                        ,'q30a'
                        ,'q30b']

    for question in negativequestions:
        dataframe[question] = dataframe[question] * -1 + 6


# TODO: replace this with Question class
def MatchQuestionIDToQuestionText(dataframe):

    questionIDToQuestionText = [('q01a', 'When doing an experiment, I try to understand how the experimental setup works. What do YOU think?')
                                ,('q01b', 'When doing an experiment, I try to understand how the experimental setup works. What would an experimental physicist say about their research?')
                                ,('q01c', 'How important for earning a good grade in this class was understanding how the experimental setup works?')
                                ,('q02a', "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment. What do YOU think?")
                                ,("q02b", "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment. What would an experimental physicist say about their research?")
                                ,("q02c", "How important for earning a good grade in this class was understanding how the measurement tools and sensors work?")
                                ,("q03a", "When doing a physics experiment, I don't think much about sources of systematic error. What do YOU think?")
                                ,("q03b", "When doing a physics experiment, I don't think much about sources of systematic error. What would an experimental physicist say about their research?")
                                ,("q03c", "How important for earning a good grade in this class was thinking about sources of systematic error?")
                                ,("q04a", "It is helpful to understand the approximations and simplifications that go into the theoretical predictions when comparing them with data. What do YOU think?")
                                ,("q04b", "It is helpful to understand the approximations and simplifications that go into the theoretical predictions when comparing them with data. What would an experimental physicist say about their research?")
                                ,("q04c", "How important for earning a good grade in this class was understanding the approximations and simplifications that are included in theoretical predictions?")
                                ,("q05a", "Whenever I use a new measurement tool, I try to understand its performance limitations. What do YOU think?")
                                ,("q05b", "Whenever I use a new measurement tool, I try to understand its performance limitations. What would an experimental physicist say about their research?")
                                ,("q05c", "How important for earning a good grade in this class was understanding the performance limitations of the measurement tools?")
                                ,("q06a", "Doing error analysis (such as calculating the propagated error) usually helps me understand my results better. What do YOU think?")
                                ,("q06b", "Doing error analysis (such as calculating the propagated error) usually helps me understand my results better.  What would an experimental physicist say about their research?")
                                ,("q06c", "How important for earning a good grade in this class was using error analysis (such as calculating the propagated error) to better understand my results?")
                                ,("q07a", "If the lab guide doesn't give clear directions for analyzing data, I am not sure how to choose an appropriate method to analyze my data. What do YOU think?")
                                ,("q07b", "If the lab guide doesn't give clear directions for analyzing data, I am not sure how to choose an appropriate method to analyze my data. What would an experimental physicist say about their research?")
                                ,("q07c", "How important for earning a good grade in this class was choosing an appropriate method for analyzing data (without explicit direction)?")
                                ,("q09a", "I am usually able to complete an experiment without understanding the equations and physics ideas that describe the system I am investigating. What do YOU think?")
                                ,("q09b", "I am usually able to complete an experiment without understanding the equations and physics ideas that describe the system I am investigating. What would an experimental physicist say about their research?")
                                ,("q09c", "How important for earning a good grade in this class was understanding the equations and physics ideas that describe the system I am investigating?")
                                ,("q10a", "I try to understand the theoretical equations provided in the lab guide. What do YOU think?")
                                ,("q10b", "I try to understand the theoretical equations provided in the lab guide. What would an experimental physicist say about their research?")
                                ,("q10c", "How important for earning a good grade in this class was understanding the theoretical equations provided in the lab guide?")
                                ,("q11a", "Computers are helpful for plotting and analyzing data. What do YOU think?")
                                ,("q11b", "Computers are helpful for plotting and analyzing data. What would an experimental physicist say about their research?")
                                ,("q11c", "How important for earning a good grade in this class was using a computer for plotting and analyzing data?")
                                ,("q12a", "When I am doing an experiment, I try to make predictions to see if my results are reasonable. What do YOU think?")
                                ,("q12b", "When I am doing an experiment, I try to make predictions to see if my results are reasonable. What would an experimental physicist say about their research?")
                                ,("q12c", "How important for earning a good grade in this class was making predictions to see if my results are reasonable?")
                                ,("q13a", "When doing an experiment I usually think up my own questions to investigate. What do YOU think?")
                                ,("q13b", "When doing an experiment I usually think up my own questions to investigate. What would an experimental physicist say about their research?")
                                ,("q13c", "How important for earning a good grade in this class was thinking up my own questions to investigate?")
                                ,("q14a", "When doing an experiment, I just follow the instructions without thinking about their purpose. What do YOU think?")
                                ,("q14b", "When doing an experiment, I just follow the instructions without thinking about their purpose. What would an experimental physicist say about their research?")
                                ,("q14c", "How important for earning a good grade in this class was thinking about the purpose of the instructions in the lab guide?")
                                ,("q15a", "Designing and building things is an important part of doing physics experiments. What do YOU think?")
                                ,("q15b", "Designing and building things is an important part of doing physics experiments. What would an experimental physicist say about their research?")
                                ,("q15c", "How important for earning a good grade in this class was designing and building things?")
                                ,("q16a", "When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor. What do YOU think?")
                                ,("q16b", "When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor. What would an experimental physicist say about their research?")
                                ,("q16c", "How important for earning a good grade in this class was overcoming difficulties without the instructor's help?")
                                ,("q17a", "A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away. What do YOU think?")
                                ,("q17b", "A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away. What would an experimental physicist say about their research?")
                                ,("q17c", "How important for earning a good grade in this class was randomly changing things to fix a problem with the experiment?")
                                ,("q18a", "Communicating scientific results to peers is a valuable part of doing physics experiments. What do YOU think?")
                                ,("q18b", "Communicating scientific results to peers is a valuable part of doing physics experiments. What would an experimental physicist say about their research?")
                                ,("q18c", "How important for earning a good grade in this class was communicating scientific results to peers?")
                                ,("q19a", "I am able to read a scientific journal article for understanding. What do YOU think?")
                                ,("q19b", "I am able to read a scientific journal article for understanding.  What would an experimental physicist say about their research?")
                                ,("q19c", "How important for earning a good grade in this class was reading scientific journal articles?")
                                ,("q20a", "Working in a group is an important part of doing physics experiments. What do YOU think?")
                                ,("q20b", "Working in a group is an important part of doing physics experiments. What would an experimental physicist say about their research?")
                                ,("q20c", "How important for earning a good grade in this class was working in a group?")
                                ,("q21a", "If I am writing a lab report, my main goal is to make conclusions based on my data using scientific reasoning. What do YOU think?")
                                ,("q21b", "If I am writing a lab report, my main goal is to make conclusions based on my data using scientific reasoning. What would an experimental physicist say about their research?")
                                ,("q21c", "How important for earning a good grade in this class was writing a lab report that made conclusions based on data using scientific reasoning?")
                                ,("q22a", "If I am writing a lab report, my main goal is to create a report with the correct sections and formatting.  What do YOU think?")
                                ,("q22b", "If I am writing a lab report, my main goal is to create a report with the correct sections and formatting. What would an experimental physicist say about their research?")
                                ,("q22c", "How important for earning a good grade in this class was writing a lab report with the correct sections and formatting?")
                                ,("q23a", "I enjoy building things and working with my hands. What do YOU think?")
                                ,("q23b", "I enjoy building things and working with my hands. What would an experimental physicist say about their research?")
                                ,("q24a", "I don't enjoy doing physics experiments. What do YOU think?")
                                ,("q24b", "I don't enjoy doing physics experiments.  What would an experimental physicist say about their research?")
                                ,("q25a", "Nearly all students are capable of doing a physics experiment if they work at it. What do YOU think?")
                                ,("q25b", "Nearly all students are capable of doing a physics experiment if they work at it.  What would an experimental physicist say about their research?")
                                ,("q26a", "If I try hard enough I can succeed at doing physics experiments.  What do YOU think?")
                                ,("q26b", "If I try hard enough I can succeed at doing physics experiments.  What would an experimental physicist say about their research?")
                                ,("q27a", "If I wanted to, I think I could be good at doing research. What do YOU think?")
                                ,("q27b", "If I wanted to, I think I could be good at doing research. What would an experimental physicist say about their research?")
                                ,("q28a", "When I approach a new piece of lab equipment, I feel confident I can learn how to use it well-enough for my purposes. What do YOU think?")
                                ,("q28b", "When I approach a new piece of lab equipment, I feel confident I can learn how to use it well-enough for my purposes. What would an experimental physicist say about their research?")
                                ,("q28c", "How important for earning a good grade in this class was learning to use a new piece of laboratory equipment?")
                                ,("q29a", "I do not expect doing an experiment to help my understanding of physics. What do YOU think?")
                                ,("q29b", "I do not expect doing an experiment to help my understanding of physics. What would an experimental physicist say about their research?")
                                ,("q30a", "The primary purpose of doing a physics experiment is to confirm previously known results. What do YOU think?")
                                ,("q30b", "The primary purpose of doing a physics experiment is to confirm previously known results. What would an experimental physicist say about their research?")
                                ,("q30c", "How important for earning a good grade in this class was confiming previously known results?")
                                ,("q31a", "Physics experiments contribute to the growth of scientific knowledge. What do YOU think?")
                                ,("q31b", "Physics experiments contribute to the growth of scientific knowledge. What would an experimental physicist say about their research?")
                                ,("q40a", "We use this statement to discard the survey of people who are not reading the questions. Please sele...-What do YOU think when doing experiments for class?")
                                ,("q40b", "We use this statement to discard the survey of people who are not reading the questions. Please sele...-What would experimental physicists say about their research?")]

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


    for q in questionIDs:
        df[q] = df[q].apply(merge)

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

        raw_df = BuildAggregateDataFrame(pre_filenames, coursetype='UpperDivision', name=n)
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

    cleanDataPipeline(dir='C:\\Users\\John\\Documents\\Visual Studio 2013\\Projects\\jinja-test\\jinja-test\\utilities\\updiv_new')

