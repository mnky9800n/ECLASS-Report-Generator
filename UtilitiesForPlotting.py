
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

"""
 The following process describes the pipeline for creating plots outside of the reporting
 environment.

 itemized survey question pipeline

 [0] def expertLikeResponseDataFrame(rawdata_df, columnIDs, CI_Calculator, grades=False):
    return data_df

 [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 

 [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
    return fig, ax

 [3] def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
    return fig, ax
"""

# #Utility functions and classes

def ReplaceMissingRowsWithZeros(dataSeries, expectedRows):
    """
    Description:
    --------------------
    Adds rows to data series with zero values.
    
    Parameters:
    --------------------
    dataSeries : pandas.Series 
    data with missing rows
    
    expectedRows : list
    expected indices of dataSeries to be compared against actual
    rows.
    
    Return:
    --------------------
    dataSeries : pandas.Series
    Input series with corrected rows with zero values.
    """
    
    
    _dataIndex = set(dataSeries.index)
    _idIndex = set(expectedRows)
    
    _diff = list(_idIndex.difference(_dataIndex))
    
    if len(_diff) > 0:
        for d in _diff:
            dataSeries.loc[d] = 0  
            
    return dataSeries

def confidenceInterval(n_respondents, n_total, n_LikertLevels=3, significanceLevel=0.05, debug=False):
    """
    Description:
    --------------------
    This calculates the confidence interval for a Likert Response with k Likert scale levels.
    
    It uses the equation:
    
    Response% +/- ConfidenceInterval = 
    
    (n_i + B/2) / (n + B) +/- sqrt( (B**2/4 + B * n_i * (1 - n_i/n)) / (n + B)**2 )
    
    where:
    
    n_i = number of respondents choosing the i-th level
    
    n = SUM(n_i, from:i=1, to:k), i.e. the total number of responses to the question
    
    k = maximum Likert scale levels (in our case, 3 after data is condensed)
    
    B = upper (alpha / k) 100th percentile of the chisquare distribution
        with 1 degree of freedom. (in this case 95%)
        
    EXAMPLE:
    --------
    Sample Question: "When doing a physics experiment, I don't think much 
    about sources of systematic error. What do YOU think?"
    
    Data:
    -----
    Strongly Agree    : 95
    Agree             : 218
    Neutral           : 196
    Disagree          : 86
    Strongly Disagree : 27
    N/A               : 11
    
    for 6 scale likert scale (Strongly Agree to Strongly Disagree + N/A)
    95% Confidence Interval, alpha=0.05, k=6:
    
    Using R:
    > qchisq(0.05/6,1, lower.tail=FALSE)
    [1] 6.960401
            
    NOTE, in R:
    
    lower.tail logical; if TRUE (default), probabilities are P[X ≤ x], 
    otherwise, P[X > x].

    
    But since this is Python:
    
    In [1]: import scipy.stats as stats

    In [2]: stats.chi2.ppf(1-0.05/6,1)
    Out[2]: 6.96040144105298
    
    NOTE, in Python:
    
    There is no 'lower.tail' to switch the range of the probability, thus
    we do '1-0.05/6'. (remember that 6 is just the number of Likert options
    in this example).
    
    Confidence Interval for percent saying "Strongly Agree":
    
    StronglyAgree% +/- CI = (95 + 6.96/2) / (633 + 6.96) +/- sqrt( (6.96**2/4 + 6.96 * 95 * (1 - 95/633)) / (633 + 6.96)**2 )
    StronglyAgree% +/- CI = 0.154 +/- 0.037
    
    Sources:
    [1] slide 13-14, http://faculty.nps.edu/rdfricke/OA4109/Lecture%209-1%20--%20Introduction%20to%20Survey%20Analysis.pdf
    [2] Accepted response, http://stackoverflow.com/questions/18070299/is-there-a-python-equivalent-of-rs-qchisq-function
    [3] scipy documentation, http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2.html
    [4] R documentation, https://stat.ethz.ch/R-manual/R-patched/library/stats/html/Chisquare.html
    
    Parameters:
    -------------------
    n_respondents : int (n_i)
    number of respondents with likert scale
    
    n_LikertLevels : int (k) : Default=3
    number of Likert Levels. Default is 3 due to combination of Likert
    responses (Strongly Dis/Agree and Dis/Agree)
    
    n_total : int (n)
    number of total responses to question
    
    significanceLevel : float (alpha = B * k) : Default=0.05
    The significance level typically known as 'alpha'. Default is 0.05.
    
    debug: Boolean : Default=False
    If True, returns B value.
    
    Returns:
    -------------------
    B : float : Default does not return
    The value returned from scipy.stats.chi2.ppf
    
    ResponsePercent : float
    Value responding with selected response.
    
    ConfidenceInterval : float
    The upper and lower bound of the interval.
    """
    if isinstance(n_respondents, int)==False:
        raise ValueError('n_respondents needs to be an integer.')
        
    if isinstance(n_LikertLevels, int)==False:
        raise ValueError('n_LikertLevels needs to be an integer.')
        
    if isinstance(n_total, int)==False:
        raise ValueError('n_total needs to be an integer.')
        
    if isinstance(significanceLevel, float)==False:
        raise ValueError('significanceLevel needs to be a float.')
        
    if significanceLevel > 1 or significanceLevel < 0:
        raise ValueError('significanceLevel needs to be between 0 and 1.')
    
    # This restriction has been relaxed because sometimes students have zero
    # expert like responses. Thus the confidence zero response still can fall
    # in some confidence interval.
    #if n_respondents <= 0:
    if n_respondents < 0:
        raise ValueError('n_respondents needs to be greater than 0.')

    if n_LikertLevels <= 0:
        raise ValueError('n_LikertLevels needs to be greater than 0.')
        
    if n_total <= 0:
        raise ValueError('n_total needs to be greater than 0.')
    
    B = stats.chi2.ppf(1-significanceLevel/n_LikertLevels, 1)
    
    ResponsePercent = (n_respondents + B/2) / (n_total + B)
    ConfidenceInterval = np.sqrt(((B**2)/4 + B * n_respondents * (1 - n_respondents/n_total))/(n_total + B)**2)
    
    if debug==True:
        return B, ResponsePercent, ConfidenceInterval
    else:
        return ResponsePercent, ConfidenceInterval

def makeNewLine(s):
    """
    Description:
    -------------------
    Replaces some central space with a newline in a 
    question string and returns it. Returns original
    string if there are no spaces.
    
    Parameters:
    -------------------
    s : string
    input string to receive newline
    
    _middleSpaceIndex : int
    index of space close to the middle of the string.
    will equal -1 if there are no spaces in the string.
    
    Returns:
    -------------------
    s : string
    string with newline added"""
    
    _middleSpaceIndex = s[0:int(len(s)/2)].rfind(' ')
    
    if _middleSpaceIndex == -1:
        pass
    else:
        s = s[0:_middleSpaceIndex] + '\n' + s[_middleSpaceIndex:]
    
    return s

def expertLikeResponseDataFrame(rawdata_df, columnIDs, CI_Calculator, grades=False):
    """
    Description:
    ---------------------
    Creates a dataframe of with the columns 'Expert Like Response' and 'Confidence Interval'
    indexed by the question ID.
    
    Parameters:
    ---------------------
    rawdata_df : pandas DataFrame
    DataFrame containing raw data of survey responses
    
    columnIDs : Question object (list)
    List of question IDs for particular question group.
    
    CI_Calculator : function
    Confidence interval function. Should return a tuple of the fraction of expert like responses
    and the confidence interval of that fraction..
    
    Returns:
    data_df : pandas Dataframe
    DataFrame with with the columns 'Expert Like Response' and 'Confidence Interval'
    indexed by the question ID.
    """
    _data = []
    
    
    for col in columnIDs:
        _n_expertLike = rawdata_df[rawdata_df[col] == 5][col].size
        _n_total = rawdata_df[col].size

        _CI = CI_Calculator(n_respondents=_n_expertLike
                           , n_total=_n_total
                           , n_LikertLevels=3
                           , significanceLevel=0.05
                           , debug=False)
        _data.append([col, _CI[0], _CI[1]])

    _data = np.array(_data)

    if grades==False:
        data_df = pd.DataFrame({'Fraction of Students with Expert Like Response':_data[:,1].astype('float64')
                               , 'Confidence Interval':_data[:,2].astype('float64')}
                              , index=[d[:-2] for d in _data[:,0]])
    else:
        data_df = pd.DataFrame({'Fraction of Students with Expert Like Response':_data[:,1].astype('float64')
                       , 'Confidence Interval':_data[:,2].astype('float64')}
                      , index=[d for d in _data[:,0]])

    return data_df

def sliceDataForItemizedPlot(df, questionListForSlicing):   
    
    pre = df.ix[questionListForSlicing]['Fraction of Students with Expert Like Response (pre)']
    post = df.ix[questionListForSlicing]['Fraction of Students with Expert Like Response (post)']
    conf = df.ix[questionListForSlicing]['Confidence Interval (pre)']
    
    return {'pre':pre, 'post':post, 'conf':conf}


# In[8]:

def createFigureForItemizedSurveyData(questions, legendLabels, title):
    
    numberOfQuestions = len(questions)
    
    fig = plt.figure(figsize=(5,numberOfQuestions))
    ax = plt.axes()
    
    # create legend box
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    ax.plot([],[],color='blue', linewidth=12.5)
    ax.plot([],[],color='red', linewidth=12.5)

    ax.legend(legendLabels, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=2)


    ax.grid(b=True, which='major', color='k'
             , alpha=0.25, linestyle='--'
            , linewidth=2)
    
    ax.set_ylim(0.5,numberOfQuestions+0.5)
    ax.set_xlim(0,1)

    # set question labels
    ax.set_yticks([y+1 for y in range(0,numberOfQuestions)])
    #questions
    y_labels = [makeNewLine(q) for q in questions]
    ax.set_yticklabels(y_labels, fontsize=14)

    ax.set_title(title, fontsize=18)
    ax.set_xlabel('Fraction of Class with Expert-like Response', fontsize=18)

    return fig, ax


# In[9]:

def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
    y_base = [y+1 for y in range(len(preData))]
    for xpre, xpost, xconf, y in zip(preData, postData, confData, y_base):
        
        #plot confidence interval
        ax.plot([xpre-xconf, xpre+xconf], [y+offset, y+offset], color=color, linewidth=12.5, alpha=0.2)
        
        #plot different lines
        ax.plot([xpre, xpost], [y+offset, y+offset], color='black', linewidth=2.5)
        
        #plot pre marker
        ax.plot(xpre, y+offset, marker='o', color=color, markersize=15, mew=1)
        
        #plot post marker
        if xpost < xpre:
            ax.plot(xpost, y+offset, marker='<', color='red', markersize=15, mew=1)
        elif xpost > xpre:
            ax.plot(xpost, y+offset, marker='>', color='green', markersize=15, mew=1)
        elif xpost == xpre:
            pass
        
    return fig, ax


def plotGradeData(data, confData, offset, fig, ax, color):
    y_base = [y+1 for y in range(len(data))]
    for x, xconf, y in zip(data, confData, y_base):
        
        #plot confidence interval
        ax.plot([x-xconf, x+xconf], [y+offset, y+offset], color=color, linewidth=12.5, alpha=0.2)
                
        #plot pre marker
        ax.plot(x, y+offset, marker='o', color=color, markersize=15, mew=1)
        
    return fig, ax

def futurePlansData(df):
    
    """
    Description:
    --------------------
    Gets data from pandas DataFrame for the Future Plans Question
    
    Parameters:
    --------------------
    df : pandas DataFrame
    any dataframe containing matched data or post data from qualtrics
    
    _q53 : list
    list of strings of the column headers in the qualtrics output for
    matched data or post data
    
    _questions : list
    question responses linked to each column
    
    _data : list
    a list of numpy ndarrays that can contain either one or two rows of
    fractional response data
    
    fractionalData : list
    a list of positive fractioned responses to the survey question
    
    Returns:
    --------------------
    ndarray : numpy ndarrary
    A 2 column, 8 row array of fractions of positive responses to the 
    items on the survey."""
    
    _q53 = ['Q53_1', 'Q53_2', 'Q53_3', 'Q53_4', 'Q53_5', 'Q53_6', 'Q53_7', 'Q53_8']

    _questions = ['physics graduate school?'
               , 'other science/math graduate school?'
               , 'a non-academic science/math/eng job?'
               , 'medical school?'
               , 'other professional school?'
               , 'teaching K-12 science/math?'
               , 'teaching college science/math/engineering?'
               , 'A non-science/math/engineering job?']
    
    _data = [(df.groupby(q).size()/df[q].size) for q in _q53]
    
    fractionData = []
    for d in _data:
        try:
            fractionData.append(d[1])
        except:
            fractionData.append(1 - d[2])
            
    return np.array([r for r in zip(fractionData, _questions)])


class Questions:
    """
    Description:
    ---------------------
    Data storage class for survey questions.
    
    If questions change this class needs to change.
    
    'x' and 'y' denote 'pre' and 'post' respectively.
    'a' denotes 'What do YOU think?' questions.
    'b' denotes 'What would an experimental physicist say about their research?' questions.
    'c' denotes 'How important for earning a good grade in this class' questions.
    The 'abc' nomenclature is based on qualtrics labeling.
    """
    
    def __init__(self):
        self.questionIDToQuestionText = [('q01a', 'When doing an experiment, I try to understand how the experimental setup works. What do YOU think?')
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

        self.questionIDToQuestionText = dict(self.questionIDToQuestionText)
        
        self.questionIDToQuestionText = {'q01a': 'When doing an experiment, I try to understand how the experimental setup works',
 'q01b': 'When doing an experiment, I try to understand how the experimental setup works',
 'q01c': '...understanding how the experimental setup works?',
 'q02a': "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment",
 'q02b': "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment",
 'q02c': '...understanding how the measurement tools and sensors work?',
 'q03a': "When doing a physics experiment, I don't think much about sources of systematic error",
 'q03b': "When doing a physics experiment, I don't think much about sources of systematic error",
 'q03c': '...thinking about sources of systematic error?',
 'q04a': 'It is helpful to understand the approximations and simplifications that go into the theoretical predictions when comparing them with data',
 'q04b': 'It is helpful to understand the approximations and simplifications that go into the theoretical predictions when comparing them with data',
 'q04c': '...understanding the approximations and simplifications that are included in theoretical predictions?',
 'q05a': 'Whenever I use a new measurement tool, I try to understand its performance limitations',
 'q05b': 'Whenever I use a new measurement tool, I try to understand its performance limitations',
 'q05c': '...understanding the performance limitations of the measurement tools?',
 'q06a': 'Doing error analysis (such as calculating the propagated error) usually helps me understand my results better',
 'q06b': 'Doing error analysis (such as calculating the propagated error) usually helps me understand my results better',
 'q06c': '...using error analysis (such as calculating the propagated error) to better understand my results?',
 'q07a': "If the lab guide doesn't give clear directions for analyzing data, I am not sure how to choose an appropriate method to analyze my data",
 'q07b': "If the lab guide doesn't give clear directions for analyzing data, I am not sure how to choose an appropriate method to analyze my data",
 'q07c': '...choosing an appropriate method for analyzing data (without explicit direction)?',
 'q09a': 'I am usually able to complete an experiment without understanding the equations and physics ideas that describe the system I am investigating',
 'q09b': 'I am usually able to complete an experiment without understanding the equations and physics ideas that describe the system I am investigating',
 'q09c': '...understanding the equations and physics ideas that describe the system I am investigating?',
 'q10a': 'I try to understand the theoretical equations provided in the lab guide',
 'q10b': 'I try to understand the theoretical equations provided in the lab guide',
 'q10c': '...understanding the theoretical equations provided in the lab guide?',
 'q11a': 'Computers are helpful for plotting and analyzing data',
 'q11b': 'Computers are helpful for plotting and analyzing data',
 'q11c': '...using a computer for plotting and analyzing data?',
 'q12a': 'When I am doing an experiment, I try to make predictions to see if my results are reasonable',
 'q12b': 'When I am doing an experiment, I try to make predictions to see if my results are reasonable',
 'q12c': '...making predictions to see if my results are reasonable?',
 'q13a': 'When doing an experiment I usually think up my own questions to investigate',
 'q13b': 'When doing an experiment I usually think up my own questions to investigate',
 'q13c': '...thinking up my own questions to investigate?',
 'q14a': 'When doing an experiment, I just follow the instructions without thinking about their purpose',
 'q14b': 'When doing an experiment, I just follow the instructions without thinking about their purpose',
 'q14c': '...thinking about the purpose of the instructions in the lab guide?',
 'q15a': 'Designing and building things is an important part of doing physics experiments',
 'q15b': 'Designing and building things is an important part of doing physics experiments',
 'q15c': '...designing and building things?',
 'q16a': 'When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor',
 'q16b': 'When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor',
 'q16c': "...overcoming difficulties without the instructor's help?",
 'q17a': 'A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away',
 'q17b': 'A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away',
 'q17c': '...randomly changing things to fix a problem with the experiment?',
 'q18a': 'Communicating scientific results to peers is a valuable part of doing physics experiments',
 'q18b': 'Communicating scientific results to peers is a valuable part of doing physics experiments',
 'q18c': '...communicating scientific results to peers?',
 'q19a': 'I am able to read a scientific journal article for understanding',
 'q19b': 'I am able to read a scientific journal article for understanding',
 'q19c': '...reading scientific journal articles?',
 'q20a': 'Working in a group is an important part of doing physics experiments',
 'q20b': 'Working in a group is an important part of doing physics experiments',
 'q20c': '...working in a group?',
 'q21a': 'If I am writing a lab report, my main goal is to make conclusions based on my data using scientific reasoning',
 'q21b': 'If I am writing a lab report, my main goal is to make conclusions based on my data using scientific reasoning',
 'q21c': '...writing a lab report that made conclusions based on data using scientific reasoning?',
 'q22a': 'If I am writing a lab report, my main goal is to create a report with the correct sections and formatting',
 'q22b': 'If I am writing a lab report, my main goal is to create a report with the correct sections and formatting',
 'q22c': '...writing a lab report with the correct sections and formatting?',
 'q23a': 'I enjoy building things and working with my hands',
 'q23b': 'I enjoy building things and working with my hands',
 'q24a': "I don't enjoy doing physics experiments",
 'q24b': "I don't enjoy doing physics experiments",
 'q25a': 'Nearly all students are capable of doing a physics experiment if they work at it',
 'q25b': 'Nearly all students are capable of doing a physics experiment if they work at it',
 'q26a': 'If I try hard enough I can succeed at doing physics experiments',
 'q26b': 'If I try hard enough I can succeed at doing physics experiments',
 'q27a': 'If I wanted to, I think I could be good at doing research',
 'q27b': 'If I wanted to, I think I could be good at doing research',
 'q28a': 'When I approach a new piece of lab equipment, I feel confident I can learn how to use it well-enough for my purposes',
 'q28b': 'When I approach a new piece of lab equipment, I feel confident I can learn how to use it well-enough for my purposes',
 'q28c': '...learning to use a new piece of laboratory equipment?',
 'q29a': 'I do not expect doing an experiment to help my understanding of physics',
 'q29b': 'I do not expect doing an experiment to help my understanding of physics',
 'q30a': 'The primary purpose of doing a physics experiment is to confirm previously known results',
 'q30b': 'The primary purpose of doing a physics experiment is to confirm previously known results',
 'q30c': '...confiming previously known results?',
 'q31a': 'Physics experiments contribute to the growth of scientific knowledge',
 'q31b': 'Physics experiments contribute to the growth of scientific knowledge',
 'q40a': 'We use this statement to discard the survey of people who are not reading the questions',
 'q40b': 'We use this statement to discard the survey of people who are not reading the questions'}

        self.questionIDs = ['q01a','q01b','q02a','q02b','q03a','q03b','q04a','q04b','q05a','q05b','q06a','q06b','q07a','q07b'
                       ,'q09a','q09b','q10a','q10b','q11a','q11b','q12a','q12b','q13a','q13b','q14a','q14b','q15a','q15b'
                       ,'q16a','q16b','q17a','q17b','q18a','q18b','q19a','q19b','q20a','q20b','q21a','q21b','q22a','q22b'
                       ,'q23a','q23b','q24a','q24b','q25a','q25b','q26a','q26b','q27a','q27b','q28a','q28b','q29a','q29b'
                       ,'q30a','q30b','q31a','q31b','q40a','q40b']

        self.negativequestions = ['q02a'
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
        
        """
        'x' and 'y' denote 'pre' and 'post' respectively.
        'a' denotes 'What do YOU think?' questions.
        'b' denotes 'What would an experimental physicist say about their research?' questions.
        'c' denotes 'How important for earning a good grade in this class' questions.
        The 'abc' nomenclature is based on qualtrics labeling.
        """
        
        self.pre_SurveyQuestions = [q+'_x' for q in self.questionIDs]

        self.post_SurveyQuestions = [q+'_y' for q in self.questionIDs]
        
        self.pre_WhatDoYouThinkQuestionIDs = [q for q in self.pre_SurveyQuestions if q.rfind('a') != -1]

        self.post_WhatDoYouThinkQuestionIDs = [q for q in self.post_SurveyQuestions if q.rfind('a') != -1]

        self.pre_ExperimentalPhysicistQuestionIDs = [q for q in self.pre_SurveyQuestions if q.rfind('b') != -1]

        self.post_ExperimentalPhysicistQuestionIDs = [q for q in self.post_SurveyQuestions if q.rfind('b') != -1]
        
        self.post_GradeQuestionIDs = [key for key,value in self.questionIDToQuestionText.items() if key.rfind('c') != -1]
        
        self.positive_negative = []
        for q in self.questionIDs:
            for nq in self.negativequestions:
                if q == nq:
                    self.positive_negative.append(1)
                    break
                else:
                    pass
            else:
                self.positive_negative.append(0)




