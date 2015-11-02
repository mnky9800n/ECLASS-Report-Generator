

import UtilitiesForPlotting
import pandas as pd
import matplotlib.pyplot as plt
from Questions import Questions

Questions = Questions()

def make_itemized_single_figure(title):

    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,17))

    fig.suptitle(title, y=0.92, fontsize=20)

    ax1.grid(b=True)
    ax2.grid(b=True)

    ax2.yaxis.tick_right()
#     n_questions = len(data)
    
    return fig, ax1, ax2

def make_eclass_item_dataframe(df):
    pre = UtilitiesForPlotting.expertLikeResponseDataFrame(rawdata_df=df
                                                , CI_Calculator=UtilitiesForPlotting.confidenceInterval
                                                , columnIDs=Questions.pre_WhatDoYouThinkQuestionIDs
                                                           +Questions.pre_ExperimentalPhysicistQuestionIDs)
    pre.columns = ['cipre','fracpre']

    post = UtilitiesForPlotting.expertLikeResponseDataFrame(rawdata_df=df
                                                , CI_Calculator=UtilitiesForPlotting.confidenceInterval
                                                , columnIDs=Questions.post_WhatDoYouThinkQuestionIDs
                                                            +Questions.post_ExperimentalPhysicistQuestionIDs)
    
    post.columns = ['cipost','fracpost']

    data = pre.join(post)
    return data

def sort_qids_by_fracpre_desc(dataframe, qids, sortby='fracpre'):
    return list(dataframe.ix[qids].sort(columns=sortby, ascending=False).index)

def plot_itemized_data(data, offset, ax1, ax2, qids, color, grades=False):
    debug = False
        
    ax1_ytick_labels = []
    ax2_ytick_labels = []

    #n_questions = len(data)
    n_questions = len(qids)
    markersize = 15

    
    for n,q in enumerate(qids):
        y = n+offset 
        
        question_text = UtilitiesForPlotting.makeNewLine(Questions.questionIDToQuestionText[q])
        
        #if n < n_questions/2:
        if n < int(n_questions/2):
            ax=ax1
            ax1_ytick_labels.append(question_text)
        else:
            ax=ax2
            ax2_ytick_labels.append(question_text)

        if grades==False:
            # plot confidence interval
            ax.plot((data.fracpre.ix[q]-data.cipre.ix[q],data.fracpre.ix[q]+data.cipre.ix[q])
                    , (y, y), linewidth=10, color=color, alpha=0.5)

            # plot difference line
            ax.plot((data.fracpre.ix[q], data.fracpost.ix[q]), (y,y), linewidth=3, color='black')

            # plot pre data point
            if grades==False:
                ax.plot(data.fracpre.ix[q], y, color=color, marker='o', markersize=markersize)
            else:
                pass

            # plot post data point
            if data.fracpost.ix[q] > data.fracpre.ix[q]:
                ax.plot(data.fracpost.ix[q], y, color=color, marker='>', markersize=markersize)
            else:
                ax.plot(data.fracpost.ix[q], y, color=color, marker='<', markersize=markersize)
        else:
            ax.plot((data.fracpost.ix[q]-data.cipost.ix[q],data.fracpost.ix[q]+data.cipost.ix[q])
                    , (y, y), linewidth=10, color=color, alpha=0.5)
            ax.plot(data.fracpost.ix[q], y, color=color, marker='o', markersize=markersize)
        
        if debug==True:
            print(data.fracpre.ix[q])
            print(Questions.questionIDToQuestionText[q])
            
    ax1.set_xlim(0,1)
    ax2.set_xlim(0,1)

    ax1.set_ylim(-1, int(n_questions/2))
    ax2.set_ylim(int(n_questions/2+1)-2, n_questions)

    ax1.set_yticks(range(0, int(n_questions/2)))
    ax2.set_yticks(range(int(n_questions/2+1)-1, n_questions))

    ax1.set_yticklabels(ax1_ytick_labels, fontsize=15)
    ax2.set_yticklabels(ax2_ytick_labels, fontsize=15)

    ax1.set_xlabel('Fraction of class with expert-like response', x=1.1, fontsize=20)

if __name__=="__main__":
    hist_raw_data = UtilitiesForPlotting.load_pre_post_data(post='postMunged_Aggregate_Data.csv', pre='preMunged_Aggregate_Data.csv')
    course_raw_data = UtilitiesForPlotting.load_pre_post_data(post='postMunged_Aggregate_Data.csv', pre='preMunged_Aggregate_Data.csv')
    course_raw_data = course_raw_data[course_raw_data.courseID=='AppState_PHY2210']

    questions = ['a','b','c']
    
    hist_data = make_eclass_item_dataframe(df=hist_raw_data)
    course_data = make_eclass_item_dataframe(df=course_raw_data)

    qids = [i for i in hist_data.index if questions[0] in i]
    qids = sort_qids_by_fracpre_desc(dataframe=hist_data, qids=qids)

    fig, ax1, ax2 = make_itemized_single_figure(title='What do YOU think?')
    plot_itemized_data(data=hist_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids, color='red')
    plot_itemized_data(data=course_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids, color='blue')    


    qids = [i for i in hist_data.index if questions[1] in i]
    qids = sort_qids_by_fracpre_desc(dataframe=hist_data, qids=qids)

    fig, ax1, ax2 = make_itemized_single_figure(title='What do EXPERTS think?')
    plot_itemized_data(data=hist_data, offset=0.2, ax1=ax1, ax2=ax2, qids=qids, color='red')
    plot_itemized_data(data=course_data, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids, color='black')    

    hist_grades = UtilitiesForPlotting.expertLikeResponseDataFrame(rawdata_df=hist_raw_data
                                                     , columnIDs=Questions.post_GradeQuestionIDs
                                                     , CI_Calculator=UtilitiesForPlotting.confidenceInterval
                                                     , grades=True)
    hist_grades.columns = ['cipost','fracpost']

    course_grades = UtilitiesForPlotting.expertLikeResponseDataFrame(rawdata_df=course_raw_data
                                                     , columnIDs=Questions.post_GradeQuestionIDs
                                                     , CI_Calculator=UtilitiesForPlotting.confidenceInterval
                                                     , grades=True)
    course_grades.columns = ['cipost','fracpost']


    qids = [i for i in hist_grades.index if questions[2] in i]
    qids = sort_qids_by_fracpre_desc(dataframe=hist_grades, qids=qids, sortby='fracpost')

    fig, ax1, ax2 = make_itemized_single_figure(title='What do GRADES think?')
    plot_itemized_data(data=hist_grades, offset=0.2, ax1=ax1, ax2=ax2, qids=qids, color='red', grades=True)
    plot_itemized_data(data=course_grades, offset=-0.2, ax1=ax1, ax2=ax2, qids=qids, color='blue', grades=True)    
