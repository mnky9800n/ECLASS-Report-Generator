
# coding: utf-8
# pylint: disable=C0321
# pylint: disable=C0303
# pylint: disable=line-too-long

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

class EmptyDataFrameError(Exception):
    pass

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

def makeNewLine(s, spliton=6):
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
    s_newline = ''
    for n,x in enumerate(s.split(' ')):
        if n < spliton:
            s_newline += x + ' '
        elif n % spliton == 0:
            s_newline += x + '\n'
        else:
            s_newline += x + ' '
    return s_newline

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

def plot_overall(hist_df, course_df):
    """
    plots aggregate scores on eclass questions
    """
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
    return ax.get_figure()

#def load_pre_post_data(pre, post):
#    """
#    loads cleaned data and returns a pandas dataframe
#    of the merged data.
#    """
#    predata = pd.read_csv(pre)
#    postdata = pd.read_csv(post)

#    return predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])


def load_pre_post_data(pre, post, course):
    """
    loads cleaned data and returns a pandas dataframe
    of the merged data.
    """

    #dtype={'ID': object}

    #predata = pd.read_csv(pre)#'preMunged_Aggregate_Data.csv')
    #postdata = pd.read_csv(post)#'postMunged_Aggregate_Data.csv')

    predata = pd.read_csv(pre, dtype={'Q3_3_TEXT':str})#'preMunged_Aggregate_Data.csv')
    postdata = pd.read_csv(post, dtype={'Q3_3_TEXT':str})#'postMunged_Aggregate_Data.csv')

    if course==True:
        #print(predata)
        #df = predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])
        #print(df)
        ##print(df)
        ##print(predata.courseID.ix[0])
        ###print(postdata.courseID.ix[0])
        ##print(predata.Q3_3_TEXT)
        ##print(postdata.Q3_3_TEXT)
        #import sys
        #sys.exit()
        pre_responses = predata.groupby('courseID').Q3_3_TEXT.count()
        post_responses = postdata.groupby('courseID').Q3_3_TEXT.count()
        return predata.merge(postdata, on=['Q3_3_TEXT', 'courseID']), pre_responses, post_responses
    else:
        ##print(predata.ix[0:10].courseID)
        ##print(postdata.ix[0:10].courseID)
        #print(predata.merge(postdata, on=['Q3_3_TEXT', 'courseID']))
        #import sys
        #sys.exit()

        #df = predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])
        #print(df)
        #import sys
        #sys.exit()
        return predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])

def save_fig(fig, save_name, svg=True, hidef=False):
    """
    saves a figure as a png or svg and can save a high def png version
    """
    if svg == True:
        fig.savefig(save_name+'.svg', bbox_inches='tight')
    else:
        fig.savefig(save_name+'.png', bbox_inches='tight', dpi=55)

    if hidef == False:
        pass
    else:
        fig.savefig(save_name+'.png', bbox_inches='tight', dpi=160)

