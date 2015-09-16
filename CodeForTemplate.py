# pylint: disable=C0321
# pylint: disable=C0303
# pylint: disable=line-too-long


q = Questions()
qids = q.pre_ExperimentalPhysicistQuestionIDs

#[q.questionIDToQuestionText[qid[:-2]] for qid in qids]


# itemized survey question pipeline
#
# [0] def expertLikeResponseDataFrame(rawdata_df, columnIDs, CI_Calculator, grades=False):
#    return data_df
#
# PIPELINE BEGINS HERE
#
# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
#
# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax
#
# [3] def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
#    return fig, ax


# In[19]:

predata = pd.read_csv('preMunged_Aggregate_Data.csv')
postdata = pd.read_csv('postMunged_Aggregate_Data.csv')
matched = predata.merge(postdata, on=['Q3_3_TEXT', 'courseID'])
historical_data = matched


course_data = matched[matched.courseID == 'CU_PHYS4430']

try:
    historical_N = max(historical_data.count())
except:
    print("historical_N could not be calculated. Please check if historical_data dataframe exists.")

try:
    course_N = max(course_data.count())
except:
    print("course_N could not be calculated. Please check if course_data dataframe exists.")
    

#history
pre = expertLikeResponseDataFrame(rawdata_df=matched
                            , columnIDs=q.pre_WhatDoYouThinkQuestionIDs+q.pre_ExperimentalPhysicistQuestionIDs
                            , CI_Calculator=confidenceInterval)
post = expertLikeResponseDataFrame(rawdata_df=matched
                            , columnIDs=q.post_WhatDoYouThinkQuestionIDs+q.post_ExperimentalPhysicistQuestionIDs
                            , CI_Calculator=confidenceInterval)
grades = expertLikeResponseDataFrame(rawdata_df=matched
                            , columnIDs=q.post_GradeQuestionIDs
                            , CI_Calculator=confidenceInterval
                            , grades=True)

df = pre.join(post, lsuffix=' (pre)', rsuffix=' (post)')
grades.columns = ['Confidence Interval (post)', 'Fraction of Students with Expert Like Response (post)']
hist_df = pd.concat([df,grades])

#course
pre = expertLikeResponseDataFrame(rawdata_df=course_data
                            , columnIDs=q.pre_WhatDoYouThinkQuestionIDs+q.pre_ExperimentalPhysicistQuestionIDs
                            , CI_Calculator=confidenceInterval)
post = expertLikeResponseDataFrame(rawdata_df=course_data
                            , columnIDs=q.post_WhatDoYouThinkQuestionIDs+q.post_ExperimentalPhysicistQuestionIDs
                            , CI_Calculator=confidenceInterval)
grades = expertLikeResponseDataFrame(rawdata_df=course_data
                            , columnIDs=q.post_GradeQuestionIDs
                            , CI_Calculator=confidenceInterval
                            , grades=True)

df = pre.join(post, lsuffix=' (pre)', rsuffix=' (post)')
grades.columns = ['Confidence Interval (post)', 'Fraction of Students with Expert Like Response (post)']
course_df = pd.concat([df,grades])


# #What Do YOU Think? [Aggregate]

# In[23]:

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
ax = data.plot(kind='bar', yerr=error, color=['blue', 'red'], alpha=0.5)
ax.set_ylim(0,1)
ax.legend(loc='lower left')

ax.set_title('Overall E-CLASS Score on\n"What do YOU think..." statements\nN(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
ax.set_ylim(0,1)
ax.legend(loc='lower left')
ax.set_xticklabels(labels=['pre','post'], rotation=0)
ax.set_ylabel('Fraction of statements\nwith expert-like responses')
del agg_df, data, error


# ##PIPELINE

# ##What do YOU think? [1]

# In[24]:

# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
qlen = len(q.pre_WhatDoYouThinkQuestionIDs)
questions = [question[:-2] for question in q.pre_WhatDoYouThinkQuestionIDs[:int(qlen/2)]]
questiontext = [q.questionIDToQuestionText[key] for key in questions]

hist_WhatDoYOUThink = sliceDataForItemizedPlot(df=hist_df, questionListForSlicing=questions)
course_WhatDoYOUThink = sliceDataForItemizedPlot(df=course_df, questionListForSlicing=questions)

# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax

fig, ax = createFigureForItemizedSurveyData(questions=questiontext, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='What do YOU think? (part 1)')

# [3] def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
#    return fig, ax

fig, ax = plotItemizedData(preData=hist_WhatDoYOUThink['pre']
                         ,postData=hist_WhatDoYOUThink['post']
                         ,confData=hist_WhatDoYOUThink['conf']
                         ,offset=0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='blue')

fig, ax = plotItemizedData(preData=course_WhatDoYOUThink['pre']
                         ,postData=course_WhatDoYOUThink['post']
                         ,confData=course_WhatDoYOUThink['conf']
                         ,offset=-0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='red')
# fig.savefig('WhatDoYouThink1.png')
# fig.clear()


# #What do YOU Think? [2]

# In[25]:

# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
qlen = len(q.pre_WhatDoYouThinkQuestionIDs)
questions = [question[:-2] for question in q.pre_WhatDoYouThinkQuestionIDs[int(qlen/2):]]
questiontext = [q.questionIDToQuestionText[key] for key in questions]

hist_WhatDoYOUThink = sliceDataForItemizedPlot(df=hist_df, questionListForSlicing=questions)
course_WhatDoYOUThink = sliceDataForItemizedPlot(df=course_df, questionListForSlicing=questions)

# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax

fig, ax = createFigureForItemizedSurveyData(questions=questiontext, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='What do YOU think? (part 2)')

# [3] def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
#    return fig, ax

fig, ax = plotItemizedData(preData=hist_WhatDoYOUThink['pre']
                         ,postData=hist_WhatDoYOUThink['post']
                         ,confData=hist_WhatDoYOUThink['conf']
                         ,offset=0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='blue')

fig, ax = plotItemizedData(preData=course_WhatDoYOUThink['pre']
                         ,postData=course_WhatDoYOUThink['post']
                         ,confData=course_WhatDoYOUThink['conf']
                         ,offset=-0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='red')
# fig.savefig('WhatDoYouThink2.png')
# fig.clear()


# #Expert vs YOU [1]

# In[26]:

# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
qlen = len(q.pre_ExperimentalPhysicistQuestionIDs)
questions = [question[:-2] for question in q.pre_ExperimentalPhysicistQuestionIDs[int(qlen/2):]]
questiontext = [q.questionIDToQuestionText[key] for key in questions]

hist_WhatDoYOUThink = sliceDataForItemizedPlot(df=hist_df, questionListForSlicing=questions)
course_WhatDoYOUThink = sliceDataForItemizedPlot(df=course_df, questionListForSlicing=questions)

# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax

fig, ax = createFigureForItemizedSurveyData(questions=questiontext, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='What do YOU think? and \nWhat would experimental physicists say \nabout their research? (part 1)')

# [3] def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
#    return fig, ax

fig, ax = plotItemizedData(preData=hist_WhatDoYOUThink['pre']
                         ,postData=hist_WhatDoYOUThink['post']
                         ,confData=hist_WhatDoYOUThink['conf']
                         ,offset=0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='blue')

fig, ax = plotItemizedData(preData=course_WhatDoYOUThink['pre']
                         ,postData=course_WhatDoYOUThink['post']
                         ,confData=course_WhatDoYOUThink['conf']
                         ,offset=-0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='red')
# fig.savefig('Expert1.png')
# fig.clear()


# In[27]:

# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
qlen = len(q.pre_ExperimentalPhysicistQuestionIDs)
questions = [question[:-2] for question in q.pre_ExperimentalPhysicistQuestionIDs[:int(qlen/2)]]
questiontext = [q.questionIDToQuestionText[key] for key in questions]

hist_WhatDoYOUThink = sliceDataForItemizedPlot(df=hist_df, questionListForSlicing=questions)
course_WhatDoYOUThink = sliceDataForItemizedPlot(df=course_df, questionListForSlicing=questions)

# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax

fig, ax = createFigureForItemizedSurveyData(questions=questiontext, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='What do YOU think? and \nWhat would experimental physicists say \nabout their research? (part 2)')

# [3] def plotItemizedData(preData, postData, confData, offset, fig, ax, color):
#    return fig, ax

fig, ax = plotItemizedData(preData=hist_WhatDoYOUThink['pre']
                         ,postData=hist_WhatDoYOUThink['post']
                         ,confData=hist_WhatDoYOUThink['conf']
                         ,offset=0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='blue')

fig, ax = plotItemizedData(preData=course_WhatDoYOUThink['pre']
                         ,postData=course_WhatDoYOUThink['post']
                         ,confData=course_WhatDoYOUThink['conf']
                         ,offset=-0.2
                         ,fig=fig
                         ,ax=ax
                         ,color='red')
# fig.savefig('Expert2.png')
# fig.clear()


# # Grades [1]

# In[28]:

# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
qlen = len(q.post_GradeQuestionIDs)
questions = [question for question in q.post_GradeQuestionIDs[:int(qlen/2)]]
questiontext = [q.questionIDToQuestionText[key] for key in questions]



# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax

fig, ax = createFigureForItemizedSurveyData(questions=questiontext, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='What do YOU think? and \nWhat would experimental physicists say \nabout their research? (part 1)')


# def plotGradeData(data, confData, offset, fig, ax, color):
#     return fig, ax
fig, ax = plotGradeData(data=hist_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                       ,confData=hist_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                       ,offset=0.2
                       ,fig=fig
                       ,ax=ax
                       ,color='blue')
fig, ax = plotGradeData(data=course_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                       ,confData=course_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                       ,offset=-0.2
                       ,fig=fig
                       ,ax=ax
                       ,color='red')
#fig.savefig('Grades1.png)
#fig.close()


# #grades [2]

# In[29]:

# [1] def sliceDataForItemizedPlot(historicalDF, courseDF, questionListForSlicing):
#    return (hist_pre, hist_post, hist_conf), (course_pre, course_post, course_conf) 
qlen = len(q.post_GradeQuestionIDs)
questions = [question for question in q.post_GradeQuestionIDs[int(qlen/2):]]
questiontext = [q.questionIDToQuestionText[key] for key in questions]



# [2] def createFigureForItemizedSurveyData(questions, legendLabels, title):
#    return fig, ax

fig, ax = createFigureForItemizedSurveyData(questions=questiontext, legendLabels=['Similiar level courses', 'Your course']
                                           ,title='What do YOU think? and \nWhat would experimental physicists say \nabout their research? (part 2)')


# def plotGradeData(data, confData, offset, fig, ax, color):
#     return fig, ax
fig, ax = plotGradeData(data=hist_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                       ,confData=hist_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                       ,offset=0.2
                       ,fig=fig
                       ,ax=ax
                       ,color='blue')
fig, ax = plotGradeData(data=course_df.ix[q.post_GradeQuestionIDs]['Fraction of Students with Expert Like Response (post)']
                       ,confData=course_df.ix[q.post_GradeQuestionIDs]['Confidence Interval (post)']
                       ,offset=-0.2
                       ,fig=fig
                       ,ax=ax
                       ,color='red')
#fig.savefig('Grades2.png)
#fig.close()


# # Gender Question

# In[30]:

# """

# 1) remove uses of matched and replace with dataframes for historical and course data
# """
# #historical_data
# #course_data

historical_gender = historical_data.groupby('Q54').Q54.size()/historical_data.Q54.size

course_gender = course_data.groupby('Q54').Q54.size()/course_data.Q54.size

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
fig.savefig('gender.png',bbox_inches='tight')


# # Future Plans

# In[31]:

"""
TODO:

1) remove uses of matched and replace with dataframes for historical and course data
"""

historical_futurePlans = futurePlansData(historical_data)

course_futurePlans = futurePlansData(course_data)

history_df = pd.DataFrame({'Similar level classes':historical_futurePlans[:,0]}
                         , index=historical_futurePlans[:,1]).astype('float64')
course_df = pd.DataFrame({'Your class':course_futurePlans[:,0]}
                        , index=course_futurePlans[:,1]).astype('float64')

futurePlans_df = history_df.join(course_df)

ax = futurePlans_df.plot(kind='barh', color=['blue', 'red'], alpha=0.75)
ax.set_title('Future Plans\nN(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
ax.set_xlim(0,1)
ax.set_xlabel('Fraction of Students')
fig = ax.get_figure()
fig.savefig('futureplans.png',bbox_inches='tight')


# # shift in physics interest

# In[32]:

"""
TODO:

1) remove uses of matched and replace with dataframes for historical and course data
"""

hist_valcnt = historical_data['Q50'].value_counts()

hist_n = historical_data['Q50'].size

course_valcnt = course_data['Q50'].value_counts()

course_n = course_data['Q50'].size

hist_interestShift = pd.DataFrame(np.array([confidenceInterval(int(val), hist_n) for val in hist_valcnt]))
hist_interestShift.columns = ['Similar level classes', 'conf (similar)']

course_interestShift = pd.DataFrame(np.array([confidenceInterval(int(val), course_n) for val in course_valcnt]))
course_interestShift.columns = ['Your class', 'conf (your)']

df = hist_interestShift.join(course_interestShift)

errors = df[['conf (similar)', 'conf (your)']].copy()
errors.columns = ['Similar level classes', 'Your class']

ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75
            , yerr=errors)
ax.set_ylim(0,1)
ax.set_xticklabels(['Decreased', 'Stayed the same', 'Increased'], rotation=45)
ax.set_ylabel('Fraction of Students')
ax.set_title('During the semester, my interest in physics. . .\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
fig = ax.get_figure()
fig.savefig('gradespart1.png',bbox_inches='tight')


# #current interest in physics

# In[33]:

"""
TODO:

1) remove uses of matched and replace with dataframes for historical and course data
"""

expectedRows=[1.,2.,3.,4.,5.,6.]

hist_valcnt = historical_data['Q49'].value_counts()

hist_valcnt = ReplaceMissingRowsWithZeros(dataSeries=hist_valcnt, expectedRows=expectedRows)
hist_n = historical_data['Q49'].size

course_valcnt = course_data['Q49'].value_counts()

course_valcnt = ReplaceMissingRowsWithZeros(dataSeries=course_valcnt, expectedRows=expectedRows)

course_n = course_data['Q49'].size

hist_interestShift = pd.DataFrame(np.array([confidenceInterval(int(val), hist_n, n_LikertLevels=6) for val in hist_valcnt]))
hist_interestShift.columns = ['Similar level classes', 'conf (similar)']

course_interestShift = pd.DataFrame(np.array([confidenceInterval(int(val), course_n, n_LikertLevels=6) for val in course_valcnt]))
course_interestShift.columns = ['Your class', 'conf (your)']

df = hist_interestShift.join(course_interestShift)

errors = df[['conf (similar)', 'conf (your)']].copy()
errors.columns = ['Similar level classes', 'Your class']

ax = df.plot(kind='bar', y=['Similar level classes', 'Your class'], color=['blue', 'red'], alpha=0.75
            , yerr=errors)
ax.set_ylim(0,1)
ax.set_xticklabels(['Very Low', 'Low', 'Moderate', 'High', 'Very High', 'N/A'], rotation=45)
ax.set_ylabel('Fraction of Students')
ax.set_title('Currrently, what is your interest in physics?\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
fig = ax.get_figure()
fig.savefig('currentinterest.png',bbox_inches='tight')


# #Delared Major

# In[34]:

questionAnswers = {1.0: 'Physics', 2.0: 'Chemistry', 3.0: 'Biochemistry', 4.0: 'Biology', 5.0: 'Engineering', 6.0: 'Engineering Physics', 7.0: 'Astronomy', 8.0: 'Astrophysics', 9.0: 'Geology/geophysics', 10.0: 'Math/Applied Math', 11.0: 'Computer Science', 12.0: 'Physiology', 13.0: 'Other Science', 14.0: 'Non-science Major', 15.0: 'Open option/Undeclared'}

expectedRows=[1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,15.]

hist_valcnt = historical_data['Q47'].value_counts()

hist_valcnt = ReplaceMissingRowsWithZeros(dataSeries=hist_valcnt, expectedRows=expectedRows)

hist_n = historical_data['Q47'].size

course_valcnt = course_data['Q47'].value_counts()

course_valcnt = ReplaceMissingRowsWithZeros(dataSeries=course_valcnt, expectedRows=expectedRows)

course_n = course_data['Q47'].size


hist_interestShift = pd.DataFrame(np.array([confidenceInterval(int(val), hist_n, n_LikertLevels=6) for val in hist_valcnt]))
hist_interestShift.columns = ['Similar level classes', 'conf (similar)']

course_interestShift = pd.DataFrame(np.array([confidenceInterval(int(val), course_n, n_LikertLevels=6) for val in course_valcnt]))
course_interestShift.columns = ['Your class', 'conf (your)']

df = hist_interestShift.join(course_interestShift)

errors = df[['conf (similar)', 'conf (your)']].copy()
errors.columns = ['Similar level classes', 'Your class']

ax = df.plot(kind='bar', y=['Similar level classes', 'Your class']
             , color=['blue', 'red'], alpha=0.75, yerr=errors)
ax.set_ylim(0,1)
ax.set_xticklabels([qstr for qstr in questionAnswers.values()], rotation=90)
ax.set_ylabel('Fraction of Students')
ax.set_title('What is your current major?\n N(yourClass) = {yourClass}, N(similarLevel) = {similarLevel}'.format(yourClass=course_N, similarLevel=historical_N))
fig = ax.get_figure()
fig.savefig('declaredmajor.png',bbox_inches='tight')
