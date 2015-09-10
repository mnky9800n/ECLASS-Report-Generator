# -*- coding: utf-8 -*-
"""
Created on Thu Apr 04 14:51:43 2013

@author: Ben
"""

import All_basic_v3_Sp15 as F

py = F.py
gridspec = F.gridspec
np = F.np
p = F.p
import scipy.stats as stats

#F.initialize_data()
tickfontsize = 11  #Set all ticks to this font size
axes_label_fontsize = 11
fontsize_1D_question_text = 10
_color1 = (1,.4,.4)
_color2 = (.4,.4,1)
_color3 = (.4,1,.4)

data_class = []
data_level = []

_legend_label_class = 'Your class'
_legend_label_level = 'Similar level classes'

def run_qualtrics(d, d_unmatched, d_level, metadata_filepath, course_row_index,plotting=True):
    """
    plotting = True runs all the plots.  If False, skips all plots but still fills the metadata dictionary, which is
                needed for the HTML template.
    """
    global data_class, data_level

    #metadata_filepath = "C:\\Users\\bmzsps\\Repos\\e-class-qualtrics-SP2015\\Data\\Intro\\Intro_Course_Summary.csv"
    F.Import.load_meta_data(metadata_filepath)

    #print F.Import.course_data
    #pick out the single row of course data to be used for this report
    single_course_data = F.Import.course_data.irow(course_row_index)
    print("course_row_index = {}".format(course_row_index))


    header_dir = "C:\\Users\\bmzsps\\Repos\\e-class-qualtrics-SP2015\\Data\\Header\\"
    pre_header_file = "header_pre_qualtrics_auto.csv"
    post_header_file = "header_post_qualtrics_auto.csv"
    F.Import.load_headers(header_dir, pre_header_file, post_header_file)

    data_dir = single_course_data["Directory"]
    if data_dir[-1] != '\\' :
        data_dir += '\\'
    pre_filename = single_course_data["Pre_Filename"]
    post_filename = single_course_data["Post_Filename"]
    #print "data_dir = \'{}\'".format(data_dir)
    F.initialize_data_clean_qualtrics(data_dir, pre_filename, post_filename, reload_data=False)

    subs = {}  # A dictionary of replacement values to be used in the generic report template

    subs['COURSE_NUMBER'] = single_course_data["Course_Number"]
    subs['CLASS_NAME'] = single_course_data["Course_Title"]
    subs['INSTITUTION'] = single_course_data["Institution"]
    subs['SEMESTER_YEAR'] = "{} {}".format(single_course_data["Semester"],single_course_data["Year"])
    subs['COURSE_LEVEL'] = single_course_data["Level"]

    #data_class = F.data # In qualtrics, we only load one course of data at a time
    data_class = d
    data_level = d_level # For now, make the two data sets the same. This needs to be fixed.

    #abort the analysis if there are no matching pre-post responses
    #matched_IDs = F.match_subset(data_class)
    if len(d) == 0 :
        print("No matching IDs in Pre and Post.  Aborting analysis of {}".format(\
                subs['CLASS_NAME']))
        return 'error'

    #get the dictionary of participation rate data
    part_dict = get_participation_rates(d_unmatched, data_class, single_course_data['Class_Size'])
    #append the participation rate meta_data to the subs dictionary
    for var in list(part_dict.keys()):
        subs[var] = str(part_dict[var])

    # set the question to be used in the example data
    # pick a positive phrased question so the raw data (disagree to agree) isn't inverted.
    question = 'q01a'

    subs['EXAMPLE_STATEMENT'] = F.header_post[question]['Question Text']



    # get grade question
    question_grade = F.change_q_type(question,'grade')
    # get grade text:
    grade_text = F.header_post[question_grade]['Question Text']
    grade_text = grade_text.split('class was')[1]
    subs['EXAMPLE_STATEMENT_GRADE'] = grade_text

    #Make the table of questions
    statement_table = make_statement_table()
    F.p.set_option('max_colwidth',120)
    subs['STATEMENT_TABLE'] = statement_table.to_html(index=False, justify='center')

    if plotting == True :

        graphics_directory = data_dir + "graphs\\"
        # if graphs directory does not exist, create it.
        if not ("graphs" in F.os.listdir(data_dir) ) :
            F.os.mkdir(graphics_directory)
        print("graphics_directory = {}".format(graphics_directory))

        pre_post_2D_hist(data_class,question, save_fig=True, save_directory=graphics_directory)
        pre_post_hist(data_class,question,save_fig=True,save_directory=graphics_directory)
        single_pre_post_change_plot(data_class,question,save_fig=True,\
                                save_directory=graphics_directory)



        mean_score_process_data(data_class)
        eclass_summary_plot(data_class,data_level,save_fig=True, save_directory=graphics_directory)


        gains_1D_compare2(data_class,data_level,"Your Class","Similar level classes",save_fig=True,\
                sortby='pre',qtype='personal', exp_nonexp='expertlike', save_directory=graphics_directory)
        gains_1D_compare_personal_professional(data_class,data_class,"Your Class","Similar level classes",save_fig=True,\
                sortby='pre',qtype1='personal',qtype2='professional',exp_nonexp='expertlike', save_directory=graphics_directory)




        #plot the addition questions at the end of the post-test
        plot_additional_questions(data_class,data_level,save_fig=True,save_directory=graphics_directory)
        plot_scatter_shift_and_pre_vs_grade(data_class, save_fig=True, save_directory=graphics_directory)
    #
       # grade_table = make_grade_table(data_class, data_level)

       # F.p.set_option('max_colwidth',120)
       # subs['GRADE_TABLE'] = grade_table.to_html(index=False, justify='center')
       # subs['GRADE_TABLE'] = subs['GRADE_TABLE'].replace('Question_Text',"How important for earning a good grade in this class was..." )

        #Make the plot of grades
        grade_table = plot_grade_table(data_class,data_level,save_fig=True, save_directory=graphics_directory)

    return subs

def run(class_name, graphics_directory):
    global data_class, data_level
    subs = {}
    
    subs['COURSE_NUMBER'] = get_readable_course_number(class_name)
    subs['CLASS_NAME'] = get_readable_course_name(class_name) 
    subs['INSTITUTION'] = get_readable_institution(class_name)
    subs['SEMESTER_YEAR'] = 'Spring 2013'
    
    data_class = F.data_subset(Class=class_name)
    data_class = F.data_subset_modified(data_class,q40a=4, q40b=4)
    
    #abort the analysis if there are no matching pre-post responses
    matched_IDs = F.match_subset_str(data_class)
    if len(matched_IDs) == 0 :
        print("No matching IDs in Pre and Post.  Aborting analysis of {}".format(\
                subs['CLASS_NAME']))
        return 'error'
            
    if class_name in F.get_class_level('non-calc-intro') :
        class_level = 'non-calc-intro'
        subs['COURSE_LEVEL'] = 'non-calculus-based introductory'
    elif class_name in F.get_class_level('calc-intro') :
        class_level = 'calc-intro'
        subs['COURSE_LEVEL'] = 'calculus-based introductory'
    elif class_name in F.get_class_level('upper-div') :
        class_level = 'upper-div'
        subs['COURSE_LEVEL'] = 'upper-division (beyond introductory)'
    else :
        print("Course did not have a valid level (non-calc-intro, calc-intro, upper-div).\n \
                    Aborting analysis.")
        return "error"
    courselist_at_level = F.get_class_level(class_level)
    data_level = F.data_subset(Class=courselist_at_level) #Make this the set of all courses of the same level.
    data_level = F.data_subset_modified(data_level,q40a = 4, q40b = 4)    
    #test_dir = "C:\\Users\\Ben\\Dropbox\\E-CLASS\\Reports to Instructors\\2013-04-03 04.36.24 PM\\Intro Physics\\Graphics\\"    
    
    
    print("subs = {}".format(subs))
    question = 'q03a'
    pre_post_2D_hist(data_class,question, save_fig=True, save_directory=graphics_directory)
    pre_post_hist(data_class,question,save_fig=True,save_directory=graphics_directory)    
    single_pre_post_change_plot(data_class,question,save_fig=True,\
                            save_directory=graphics_directory)
    gains_1D_compare2(data_class,data_level,"Your Class","Similar Level",save_fig=True,\
            sortby='pre',qtype='personal', exp_nonexp='expertlike', save_directory=graphics_directory)                          
    gains_1D_compare_personal_professional(data_class,data_class,"Your Class","Similar Level",save_fig=True,\
            sortby='pre',qtype1='personal',qtype2='professional',exp_nonexp='expertlike', save_directory=graphics_directory)

    subs['EXAMPLE_STATEMENT'] = F.header_post[question]['Question Text']

    
    
    #get grade text:
    grade_text = F.header_post['q03a'.replace('a','c')]['Question Text']
    grade_text = grade_text.split('class was')[1]
    subs['EXAMPLE_STATEMENT_GRADE'] = grade_text    

                    
    #plot the addition questions at the end of the post-test
    plot_additional_questions(data_class,data_level,save_fig=True,save_directory=graphics_directory)
    plot_scatter_shift_and_pre_vs_grade(class_name, save_fig=True, save_directory=graphics_directory)
#    class_table = F.course_goals(data_class)
#    class_table.columns = ['Question_Text', 'Mean (Class)', 'Std Dev. (Class)']
#    level_table = F.course_goals(data_level)
#    level_table.columns = ['Question_Text','Mean (Level)', 'Std Dev. (Level)']
    grade_table = make_grade_table(data_class, data_level)
#    print grade_table
    F.p.set_option('max_colwidth',120)    
    subs['GRADE_TABLE'] = grade_table.to_html(index=False, justify='center')
    subs['GRADE_TABLE'] = subs['GRADE_TABLE'].replace('Question_Text',"How important for earning a good grade in this class was..." )

    #Make the plot of grades
    plot_grade_table(data_class,data_level,save_fig=True, save_directory=graphics_directory)

    
    #Make the table of questions
    statement_table = make_statement_table()
    F.p.set_option('max_colwidth',120)    
    subs['STATEMENT_TABLE'] = statement_table.to_html(index=False, justify='center')    
    
    return subs    
    #return (grade_table,subs)
#    return F.p.concat([class_table,level_table])
    #print make_grade_table(data_class=data_class,data_level=data_level)    
    
def get_readable_course_name(class_name) :   
    single_class_metadata = F.data_subset_modified(datain=F.course_data, Instructor_html=class_name)
    return single_class_metadata['Course_Title'].values[0]

def get_readable_institution(class_name) :   
    single_class_metadata = F.data_subset_modified(datain=F.course_data, Instructor_html=class_name)
    return single_class_metadata['Institution'].values[0]
    
def get_readable_course_number(class_name) :   
    single_class_metadata = F.data_subset_modified(datain=F.course_data, Instructor_html=class_name)
    return single_class_metadata['Course_Number'].values[0]

def get_participation_rates(data_unmatched, data_matched,enrollment) :
    """
    data_unmatched = imported class data that has been cleaned up but not been matched, data_raw_nodups.
    data_matched = class data that has been matched
    enrollment = number of students in the course.
    """

#    data_matched_class = F.data_query(data,Class=class_name,Semester=semester,\
#            Year=year)
    #data_non_matched = F.data_raw_nodups
#    print "matches = {}, raw = {}".format(len(data_matched_class),len(data_raw_class))

    pre_unmatched = F.data_query(data_unmatched,PrePost='Pre')
    post_unmatched = F.data_query(data_unmatched,PrePost='Post')

    #pre_raw = F.remove_duplicates(pre_raw)
    #post_raw = F.remove_duplicates(post_raw)

    part_dict = {}    #participation dictionary
    part_dict["NUMBER_VALID_PRE"] = len(pre_unmatched)
    part_dict["NUMBER_VALID_POST"] = len(post_unmatched)
    part_dict["NUMBER_MATCHED"] = len(data_matched)/2

    #class_meta_data = basic.data_query(basic.course_data,Semester=semester,Year=year,Instructor_html=class_name)
    #num_students = class_meta_data['Num_students'].irow(0)
    part_dict["NUMBER_STUDENTS_IN_CLASS"] = "{:.0f}".format(enrollment) #just get the value
    fraction_participating =  1.0*part_dict["NUMBER_MATCHED"]/enrollment
    part_dict["FRACTION_PARTICIPATING"] = "{:.2f}".format(fraction_participating)
    return part_dict

def eclass_summary_plot(data_class,data_level,save_fig=False, save_directory='empty') :
    """
    Creates a bar graph with the %agreement with expertlike for Class and SImilar
    Level courses.  Have error bars.
    """
    #Get the pre and post means with error bars
    #0=pre_mean, 1=post_mean, 2=pre_error, 3=post_error
    class_pre_post = mean_score_process_data(data_class)
    level_pre_post = mean_score_process_data(data_level)

    fig = py.figure(figsize=(5.5,3.5))
    ax=fig.add_subplot(111)

    width = 0.3
    ind = np.array([0,1])
    color1 = _color1
    color2 = _color2
#    data_err = np.array([0,0])

    class_pre_post = np.array(class_pre_post)
    level_pre_post = np.array(level_pre_post)
    error_kw = {"elinewidth":1,"capsize":6,"capthick":1,"ecolor":'k'}
    #plot the class data
    bar1 = ax.bar( ind - width,class_pre_post[0:2],width=width,color=color1,\
            yerr=class_pre_post[2:4],error_kw=error_kw)
    #plot the level data
    bar2 = ax.bar( ind,level_pre_post[0:2],width=width,color=color2,\
            yerr=level_pre_post[2:4],error_kw=error_kw)

    voffset = 0.06
    ax.annotate("{:.2f}".format(class_pre_post[0]),xy=(0-width/2,class_pre_post[0] + voffset),ha='center',va='bottom')
    ax.annotate("{:.2f}".format(class_pre_post[1]),xy=(1-width/2,class_pre_post[1] + voffset),ha='center',va='bottom' )
    ax.annotate("{:.2f}".format(level_pre_post[0]),xy=(0+width/2,level_pre_post[0] + voffset),ha='center',va='bottom' )
    ax.annotate("{:.2f}".format(level_pre_post[1]),xy=(1+width/2,level_pre_post[1] + voffset),ha='center',va='bottom' )

    ax.set_ylim(0,1)
    ax.set_xlim(-0.5,1.5)
    ax.set_xticks([0,1])
    ax.set_xticklabels(['Pre','Post'],\
                        fontsize = axes_label_fontsize, rotation=0, horizontalalignment='center')
    ax.set_ylabel('Fraction of statements\nwith expert-like responses',multialignment='center')
#    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.grid(which='major',axis='y',color='gray',linestyle='dashed')
    n_class = len(data_class)/2
    n_level = len(data_level)/2
    legend_label = ( '{} N = {}'.format(_legend_label_class,n_class),'{} N = {}'.format(_legend_label_level,n_level))
    ax.legend((bar1[0],bar2[0]),legend_label,\
              loc=3,fontsize='10',ncol=2,bbox_to_anchor = (0,1.02),borderaxespad=0.)
    title = '   Overall E-CLASS Score on\n"What do YOU think..." statements'
    py.suptitle(title,fontsize=11,fontweight='bold')
    py.tight_layout()
    py.subplots_adjust(top=0.8,right=0.97)

    if save_fig == True :
        fig.savefig(save_directory + "Overall_ECLASS_Summary.png", \
                    dpi=300,pad_inches=0)

def mean_score_process_data(data_in):
    '''Calculates the mean personal score'''

#    columns = data_in.columns
    q_list = F.get_q_list(qtype='personal')
    explike_fraction_pre = []
    explike_fraction_post = []
    d = data_in.copy()
    #Change the answers for negatively worded-questions to align with positively-
    #worded questions
    for q in q_list:
        if q=='q30c' or q=='q30d':
            d.ix[:,q] = d.loc[:,q].apply(np.float)
        if F.header_post[q][3] == 'n':
            d.ix[:,q] = -(d.loc[:,q]-3)+3
    total_qs = len(q_list)

    #To avoid the horror of dividing by zero
    if total_qs ==0:
        print('No question data were inputted')
        return

    d_pre  = F.data_query(d,PrePost='Pre')
    d_post = F.data_query(d,PrePost='Post')
#    print "len(d_post) = {}".format(len(d_post))

    for stud in d_pre.index:
        exp_total_pre = 0
        stud_response_pre = d_pre.loc[stud,q_list]
        values_pre = stud_response_pre.value_counts()
        # Unfortunately, must use for loop to count the expertlike responses
        # since there are cases when a
        for ind in values_pre.index:
            if ind == 5 or ind == 4: exp_total_pre += values_pre[ind]
        explike_pre = float(exp_total_pre)/float(total_qs) + 1e-10
        explike_fraction_pre.append(explike_pre)

    for stud in d_post.index:
        exp_total_post = 0
        stud_response_post = d_post.loc[stud,q_list]
        values_post = stud_response_post.value_counts()
        for ind in values_post.index:
            if ind == 5 or ind == 4: exp_total_post += values_post[ind]
        explike_post = float(exp_total_post)/float(total_qs) + 1e-10
        explike_fraction_post.append(explike_post)

    mean_pre = np.array(explike_fraction_pre).mean()
    mean_post = np.array(explike_fraction_post).mean()
#    hist_data, bins_data = np.histogram(explike_perc,bins=10,range=(-.01,1.1))

    ###CAlCULATE THE ERROR IN THIS MEAN

    pre_shift_dataframe = gains_1D_process_data(d,qtype='personal',q_list=q_list)

    pre_expert_series = pre_shift_dataframe['pre_expert']
    shift_expert_series = pre_shift_dataframe['shift_expert']
    pre_nonexpert_series = pre_shift_dataframe['pre_nonexpert']
    shift_nonexpert_series = pre_shift_dataframe['shift_nonexpert']
    pre_neutral_series = pre_shift_dataframe['pre_neutral']
    shift_neutral_series = pre_shift_dataframe['shift_neutral']

    num_matched_series = pre_expert_series + pre_neutral_series + pre_nonexpert_series
#    print "num_matched_series = {}".format(num_matched_series)

    #need post info for calculating the errorbars in the post
    post_expert_series = pre_expert_series + shift_expert_series
    post_nonexpert_series = pre_nonexpert_series + shift_nonexpert_series
    post_neutral_series = pre_neutral_series + shift_neutral_series

    num_matched_series_post = post_expert_series + post_neutral_series + post_nonexpert_series
#    print "post_neutral_series = {}".format(post_neutral_series)
#    print "num_matched_series_post = {}".format(num_matched_series_post)
#
    error_list_pre = []
    error_list_post = []
    for q in q_list :
        #calculate the pre uncertainty
        expert_unc_pre, nonexpert_unc = F.uncertainty_1D_fast(fav_act=pre_expert_series[q], \
                    unfav_act=pre_nonexpert_series[q], num_matched=num_matched_series[q])
        #calculate the post uncertainty
        expert_unc_post, nonexpert_unc = F.uncertainty_1D_fast(fav_act=post_expert_series[q], \
                    unfav_act=post_nonexpert_series[q], num_matched=num_matched_series_post[q])
        norm_unc_pre = 1.0*expert_unc_pre/num_matched_series[q]  #normalize uncertainty so it is fractional
        norm_unc_post = 1.0*expert_unc_post/num_matched_series[q] #normalize uncertainty so it is fractional
        error_list_pre.append(norm_unc_pre)
        error_list_post.append(norm_unc_post)
    error_list_pre = np.array(error_list_pre)

#    print "error_list_post = {}".format(error_list_post)

    error_list_post = np.array(error_list_post)
    total_error_pre = np.sqrt((error_list_pre**2).sum())/len(error_list_pre) #sum in quadrature, then take sqrt, and then divide by N
    total_error_post = np.sqrt((error_list_post**2).sum())/len(error_list_post)#sum in quadrature, then take sqrt, and then divide by N
    sigma_scale = 1.95996 #gives the 95% confidence interval
    total_error_pre *= sigma_scale
    total_error_post *= sigma_scale

    return (mean_pre,mean_post,total_error_pre,total_error_post)

def single_pre_post_change_plot(data, question, save_fig=False, save_directory='empty'):
    """
    Creates a pre/post change plot for one single question as an example
    data should be restricted to the student population of interest, i.e., 
    it should be the class of interest.
    """
    #process the data
    pre_shift_dataframe = gains_1D_process_data(data,[question],qtype='personal')
        
    pre_expert_series = pre_shift_dataframe['pre_expert']
    shift_expert_series = pre_shift_dataframe['shift_expert']
    pre_nonexpert_series = pre_shift_dataframe['pre_nonexpert']
#    shift_nonexpert_series = pre_shift_dataframe['shift_nonexpert']
    pre_neutral_series = pre_shift_dataframe['pre_neutral']
    
    pre_series = pre_expert_series
    shift_series = shift_expert_series    
    
    num_matched_series = pre_expert_series + pre_neutral_series + pre_nonexpert_series
    
    #Create the figure    
    fig_size = (6.5,1.25)
    gridspec_width_ratio = [5,4] 
    fig = py.figure(figsize=fig_size)
    gs = gridspec.GridSpec(1, 2,width_ratios=gridspec_width_ratio)
    ax = fig.add_subplot(gs[0])
    #ax = fig.add_subplot(121)    
    ax.set_xlim(0,1)  
    
    #Add vertical grid lines    
    ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')      
    ax.set_ylim(-1, 1) #There is only one question to plot...

    counter = 0 #The y position of the bar
    offset = 0 #The y position offset of the bar (if there was more than one bar)    
    q = question
#        num_matched = pre_expert_series[q] + pre_neutral_series[q] + pre_nonexpert_series[q]
        
    
    pre_norm = pre_series[q]*1.0/num_matched_series[q]
    shift_norm = shift_series[q]*1.0/num_matched_series[q]
#    print q + ", N = " + str(num_matched_series[q]) + ", pre_norm = " + str(pre_norm) + ", shift_norm = " + str(shift_norm)

    colour = 'b' 
    #plot the horizontal grid line        
    ax.plot([0,1],[counter,counter], '--', color='0.8')
    #plot the marker at the pre position        
    ax.plot([pre_norm], [counter+offset], 'o',color=colour)
    #plot the arrow if there is a nonzero shift        
    if shift_norm != 0.0 :        
        ax.arrow(pre_norm, counter+offset, shift_norm, 0, \
                 length_includes_head = True, head_width = 0.4, head_length = 0.015)

    expert_unc, nonexpert_unc = F.uncertainty_1D_fast(fav_act=pre_expert_series[q], \
                unfav_act=pre_nonexpert_series[q], num_matched=num_matched_series[q])
    
    uncertainty = expert_unc    
    uncertainty_norm = uncertainty/num_matched_series[q]
    
    sigma_scale = 1.95996 #gives the 95% confidence interval for 1D distribution
    uncertainty_norm *= sigma_scale #scale uncertainty to a 95% confidence interval
        
    ax.plot([pre_norm - uncertainty_norm, pre_norm + uncertainty_norm], \
            [counter+offset, counter+offset],color=colour,lw=6,alpha=0.2 )        
    title = wrap_text2(F.header_pre[q]['Question Text'],40)
    ax.text(1.02, counter, title,fontsize=10,verticalalignment='center')
    py.xlabel('Fraction of class with expert-like response', fontsize=axes_label_fontsize)

    #rescale the tick font size and remove the y tick labels
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(tickfontsize)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(tickfontsize)
        tick.label1.set_visible(False)
    
    py.subplots_adjust(bottom=0.4, left=.02, right=.99, top=.75, hspace=.1)
    qtext = 'What do YOU think?'
    py.suptitle(qtext +  '  N = '+str(num_matched_series[q]),fontsize=11)
    py.show()
    
    if save_fig == True :
        fig.savefig(save_directory + "Single_Question_pre_post_change.png", \
                    dpi=300,pad_inches=0)
    
    return ax
    
def make_statement_table() :
    q_list = F.get_q_list(qtype='personal')
    q_list_grade = F.get_q_list(qtype='grade')
    q_number_list = []
    q_personal_statement_list = []
    q_grade_statement_list = []
    for q in q_list :
        q_number_list.append(q[1:3].lstrip('0'))  #pick out the 2nd and 3rd characters AND leading zero if necessary.v
        q_personal_statement_list.append(F.header_post[q]['Question Text'])        
        q_grade = q.replace('a','c')   
        if q_grade in q_list_grade :
            q_grade_statement = F.header_post[q_grade]['Question Text']
            q_grade_statement = q_grade_statement.split('class was')[1]
            q_grade_statement = '...' + q_grade_statement
            q_grade_statement_list.append(q_grade_statement)
        else: 
            q_grade_statement_list.append('NA')
    q_number_Series = p.Series(q_number_list, name='Number')
    q_personal_statement_Series = p.Series(q_personal_statement_list, name='Personal/Professional Statement')
    q_grade_statement_Series = p.Series(q_grade_statement_list, name='How important for earning a good grade in this class was...')
#    q_df = F.p.DataFrame({'Number':q_number_Series, \
#                          'Personal/Professional Statement':q_personal_statement_Series, \
#                          'How important for earning a good grade in this class was...': \
#                              q_grade_statement_Series})
    q_df = p.concat([q_number_Series,q_personal_statement_Series, q_grade_statement_Series],axis=1)
    return q_df

def wrap_text2(text,line_len=60):    
    words = text.split(' ')
    linelist = [''] #start off with a one line empty list
    counter = 0    
    for word in words :
        if len(linelist[counter]) + 1 + len(word) <= line_len :
            if len(linelist[counter]) > 0  :
                linelist[counter] += ' '  #Add a space before appending the word unless the line is empty
            linelist[counter] += word  #Append the word
        else :
            linelist.append(word) #create a new line and add the new word
            counter += 1
    
    return '\n'.join(linelist) #join all the lines together with no separator
    
def plot_additional_questions(data_class,data_level,save_fig=False,save_directory='empty'):
    
    #Physics_Interest
    column_name='Q49'
    response_type = 'categorical'
    response_dict = {1:"Very Low", 2:"Low", 3:"Moderate", 4:"High", 5:"Very High"}
    figsize = (4.5,3)    
    plot_class_vs_level_hist(data_class,data_level, column_name, \
        response_type,response_dict,figsize,save_fig, save_directory)
       
    
    #Interest_Change
    column_name='Q50'
    response_type = 'categorical'
    response_dict = {1:"Increased", 2:"Stayed the same", 3:"Decreased"}
    figsize = (4.5, 3)    
    plot_class_vs_level_hist(data_class,data_level, column_name, \
        response_type,response_dict,figsize,save_fig, save_directory)


    #Current_Major
    column_name='Q47'
    response_type = 'categorical'
    response_dict = {1:"Physics", 2:"Chemistry", 3:"Biochemistry", \
                4:"Biology", 5:"Engineering", \
                6:"Engineering Physics", 7:"Astronomy", 8:"Astrophysics",\
                9:"Geology/Geophysics", \
                10:"Math/Applied Math", 11:"Computer Science", 12:"Physiology",\
                13:"Other Science", \
                14:"Non-science major", 15:"Open Option/undeclared"}
    figsize=(6.5,4.5)
    plot_class_vs_level_hist(data_class,data_level, column_name, \
        response_type,response_dict,figsize,save_fig, save_directory)

    #Future_Major
    column_name='Q48'
    response_type = 'categorical'
    #response_dict is same as for Current Major
    figsize=(6.5,4.5)
    plot_class_vs_level_hist(data_class,data_level, column_name, \
        response_type,response_dict,figsize,save_fig, save_directory)

    #Gender
    column_name='Q54'
    response_type = 'categorical'
    response_dict = {1:"Female", 2:"Male", 3:"Prefer not to say"}
    figsize=(6.5,4.5)
    plot_class_vs_level_hist(data_class,data_level, column_name, \
        response_type,response_dict,figsize,save_fig, save_directory)

    #future plans
    column_name='Future'
    response_type = 'categorical'
    response_dict = {1:"Physics grad school", 2:"Other Math/Sci Grad School", 3:"Non-Academic STEM Job", \
                 4:"Medical school", 5:"Other prof. school", 6:"K-12 STEM teaching", 7:"College STEM teaching", \
                 8:"Non-STEM job"}
    figsize=(6.5,4.5)

    #need to combine responses from the following 8 questions into a single data frame
    future_data_class = future_plans_combine_data(data_class)
    future_data_level = future_plans_combine_data(data_level)

    #Append the header to include the future plans question
    F.header_post.loc['Question Text','Future'] = 'Future Plans'

    plot_class_vs_level_hist(future_data_class,future_data_level,column_name,response_type,response_dict, \
                             figsize, save_fig, save_directory)

def future_plans_combine_data(data_in) :
    """
    Combines data from the 8 sub-questions Q53_1 to Q53_8 into a single data array for plotting.
    """

    #if the value is 1, the response was "True"
    #create smaller data frames that combine.
    physics_grad_school = F.data_query(data_in,Q53_1=1)
    if len(physics_grad_school) > 0 :
        physics_grad_school.loc[:,'Future'] = 1

    other_math_sci_grad_school = F.data_query(data_in,Q53_2=1)
    if len(other_math_sci_grad_school) > 0 :
        other_math_sci_grad_school.loc[:,'Future'] = 2

    non_academic_math_sci_eng_job = F.data_query(data_in,Q53_3=1)
    if len(non_academic_math_sci_eng_job) > 0 :
        non_academic_math_sci_eng_job.loc[:,'Future'] = 3

    medical_school = F.data_query(data_in,Q53_4=1)
    if len(medical_school) > 0 :
        medical_school.loc[:,'Future'] = 4

    other_prof_school = F.data_query(data_in,Q53_5=1)
    if len(other_prof_school) > 0 :
        other_prof_school.loc[:,'Future'] = 5

    teaching_K12_sci_math = F.data_query(data_in,Q53_6=1)
    if len(teaching_K12_sci_math) > 0 :
        teaching_K12_sci_math.loc[:,'Future'] = 6

    teaching_college_sci_math_eng = F.data_query(data_in,Q53_7=1)
    if len(teaching_college_sci_math_eng) > 0 :
        teaching_college_sci_math_eng.loc[:,'Future'] = 7

    non_sci_math_eng_job = F.data_query(data_in,Q53_8=1)
    if len(non_sci_math_eng_job) > 0 :
        non_sci_math_eng_job.loc[:,'Future'] = 8

    future_data = p.concat([physics_grad_school, other_math_sci_grad_school,\
                           non_academic_math_sci_eng_job,medical_school, other_prof_school, \
                           teaching_K12_sci_math, teaching_college_sci_math_eng, \
                           non_sci_math_eng_job])
    return future_data.copy()
   
def plot_class_vs_level_hist(data_class,data_level, column_name, response_type,\
        response_dict,figsize=(4.5,3.), save_fig=False, save_directory='empty'):
    """
    data_class is a pandas DataFrame with all student responses for a particular course
    
    data_level is a pandas DataFrame with all student responses for that level of course.

    column_name is the question name, like 'Physics Interest' or 'Interest_Change'
    
    response_type is either "categorical" or "numerical"

    response_dict is of the form {survey_response1:readable_response1,... }
    """        
    
    post_class = F.data_query(data_class, PrePost='Post')
    phys_interest_class = post_class[column_name]
#    print "phys_interest_class" + str(phys_interest_class)
    if response_type == 'numerical' :    
        phys_interest_class = phys_interest_class.replace('NaN',0.)        
        phys_interest_class = phys_interest_class.apply(np.float)
    post_level = F.data_query(data_level, PrePost='Post')
    phys_interest_level = post_level[column_name]
#    print phys_interest_level
    if response_type == 'numerical' :        
        phys_interest_level = phys_interest_level.replace('NaN',0.)        
        phys_interest_level = phys_interest_level.apply(np.float)
    
    
    fig=py.figure(figsize=figsize)
    gs=gridspec.GridSpec(1,1)
    ax=fig.add_subplot(gs[0])
    ind=F.np.arange(1,1+len(response_dict))
    width = 0.3    
    
    color1 = _color1
    color2 = _color2    
    
    if response_type == "categorical" :
        hist1, hist_labels = interleaved_hist_base_categorical(ax,seriesin=phys_interest_class,\
                        width=width,shift=-width,color=color1,\
                        response_dict=response_dict, norm=True)
        hist2, hist_labels = interleaved_hist_base_categorical(ax,seriesin=phys_interest_level,\
                        width=width,shift=0,color=color2,\
                        response_dict=response_dict, norm=True)        
                    
    elif response_type == "numerical" :
        hist1 = interleaved_hist_base(ax,seriesin=phys_interest_class,width=width,shift=-width,color=color1,norm=True)
        hist2 = interleaved_hist_base(ax,seriesin=phys_interest_level,width=width,shift=0,color=color2,norm=True)     
        hist_labels = ind
        
        
    title = F.header_post[column_name][0]+'\nN (Class) = '+str(len(phys_interest_class))+', N (Level) = '+str(len(phys_interest_level))

    py.title(title,fontsize = axes_label_fontsize) 
    ax.set_ylabel('Fraction of Students',fontsize = axes_label_fontsize)
        
    
#    print "hist_labels = {}".format(hist_labels)    
    ax.set_xticks(list(range(1, 1 + len(response_dict))))
    xlabels = []
    for lab in hist_labels:
        xlabels.append(response_dict[lab])
    ax.set_xticklabels(xlabels,\
                        fontsize = axes_label_fontsize, rotation=45, horizontalalignment='right')
    py.xlim(.5,0.5+len(response_dict))
#    gs.tight_layout(fig,rect=[0,0,.8,1])
    py.tight_layout()
    py.subplots_adjust(right=.75)
    lgd=ax.legend((hist1[0],hist2[0]),('Class','Level'),loc=10,bbox_to_anchor = (.7, .5, 1., .102),prop={"size":12})
    
    if save_fig == True:
        fig.savefig(save_directory + column_name +'.png', dpi=300)
#        fig.savefig(save_directory + column_name +'.png', bbox_extra_artists=(lgd,),bbox_inches='tight', dpi=300) 
    
def interleaved_hist_base(ax,seriesin,width,shift,color,norm=True):
    """
    
    """    
    total_num=1.0*len(seriesin)
    ind = F.np.arange(1,6)
    hist_data, bins_data = F.np.histogram(seriesin,bins=5,range=(0.5,5.5))
#    print hist_data
#    print "hist_data.sum() = {}".format(hist_data.sum())
#    print "total_num = {}".format(total_num)
    data_err = [0,0,0,0,0]
    data_err =  total_num*(hist_data/total_num)*(1-hist_data/total_num)   #as a variance
    data_err = F.np.sqrt(data_err) #as a standard deviation
    
#    print bins_data
#    print "ind = {}".format(ind)
    if norm == True:
        hist_data = 1.0*hist_data/total_num
        data_err = 1.0*data_err/total_num
#        print "data_err = {}".format(data_err)
    hist = ax.bar(ind+shift,hist_data,width=width,color=color,yerr=data_err,ecolor='k')
    return hist
    
def interleaved_hist_base_categorical(ax,seriesin,width,shift,color,response_dict,norm=True):
    """
    
    """    
    keys = list(response_dict.keys())
#    print "keys = {}".format(keys)
#    print "len(keys) = {}".format(len(keys))
    all_cats = F.p.Series(F.np.zeros(len(keys)), index=keys)
#    print "all_cats = {}".format(all_cats)
    
    total_num=1.0*len(seriesin)
    hist_data = seriesin.value_counts()
#    print "hist_data = {}".format(hist_data)    
    
    hist_data_all_cats = hist_data + all_cats    
    hist_data_all_cats = hist_data_all_cats.fillna(0)
    hist_data_all_cats = hist_data_all_cats[keys]
    
#    print "hist_data_all_cats = {}".format(hist_data_all_cats)
    hist_cats_all = hist_data_all_cats.index
#    print "hist_cats_all = ".format(hist_cats_all)

#    print hist_data_all_cats
#    print "hist_data_all_cats.sum() = {}".format(hist_data_all_cats.sum())
#    print "total_num = {}".format(total_num)
    
    data_err =  total_num*(hist_data_all_cats/total_num)*(1-hist_data_all_cats/total_num)   #as a variance
    data_err = F.np.sqrt(data_err) #as a standard deviation
#    for x in range(len(data_err)):
#        data_err[x]= total_num*(hist_data[x]/total_num)*(1-hist_data[x]/total_num)
#    
#    print hist_cats_all
    ind = F.np.arange(1,1+len(hist_data_all_cats))    
    
    if norm == True:
        hist_data_all_cats = 1.0*hist_data_all_cats/total_num
        data_err = 1.0*data_err/total_num
#        print "data_err = {}".format(data_err)
    hist = ax.bar(ind+shift,hist_data_all_cats,width=width,color=color,yerr=data_err,ecolor='k')
    return (hist, hist_cats_all)     
    
####PLOTS FROM TAKAKO

def pre_post_2D_hist(datain,q,save_fig=False, save_directory='empty'):
    '''pre/post 2D hist for one question'''
    fig_size = (4.5,4.5)    
    # Assume data is already clean
    #d = F.data_subset_modified(datain,q40a=4,q40b=4)             #get the subset of people who have taken the course and answered the validation question
    preresponses = F.data_query(datain,PrePost='Pre')    #get preresponses
    postresponses = F.data_query(datain,PrePost='Post')  #get postresponses
    matched = F.match_subset(datain)                               #get the matching SIDs
    num_matched = len(matched) 
    #fig = py.figure(figsize=fig_size)
    #ax = fig.add_subplot(1,1,1)

    #just pick out the SID_unique and question columns
    pre = preresponses.loc[:,['SID_unique',q]]
    post = postresponses.loc[:,['SID_unique',q]]

    #fill any NAN.
    pre = pre.fillna(0)
    post = post.fillna(0)

    #this function doesn't return anything...delete that stuff.
    #percentage, CS_per, num_matched = F.pre_post_2D_hist(preresponses,postresponses,savefigs=False)
    fig, ax = F.pre_post_2D_hist(pre,post,savefigs=False)

    #ax = gca()
    #edit the default plot axes and labels...
    title= F.header_pre[q][0]+ ' '+ F.header_pre[q][1] +',  N='+str(num_matched)
    #ax.set_title(wrap_text2(title,50),fontsize=axes_label_fontsize)
    ax.set_title("")
    py.suptitle(wrap_text2(title,50),fontsize=axes_label_fontsize)
#    py.title('Personal')

    ax.set_yticks([1,2,3,4,5])
    ax.set_xticks([1,2,3,4,5])
    ax.set_xticklabels(['Strongly\nDisagree', 'Disagree', 'Neutral','Agree','Strongly\nAgree'],\
       rotation=45,horizontalalignment='right',fontsize=axes_label_fontsize)
    ax.set_yticklabels(['Strongly\nDisagree', 'Disagree', 'Neutral','Agree','Strongly\nAgree'],\
       rotation=0,horizontalalignment='right',fontsize=axes_label_fontsize)

    ax.set_xlabel('Pre',weight='bold')
    ax.set_ylabel('Post',weight='bold')

    #fig.tight_layout()
    #py.show()
    #print ax.get_xlabel()
    if save_fig == True :         
        py.savefig(save_directory + "Single_Question_2D_pre_post_Hist.png",dpi=300,bbox_inches='tight')
#        py.close()
    
    return     
    
def pre_post_hist(datain,q,save_fig=False, save_directory='empty'):
    '''pre/post interleaved histogram'''
    
    figsize=(4.5,3.5)    
    d=F.data_query(datain,q40a=4,q40b=4)
    num_bars=2
    width=round(1.0/(num_bars+.5),2)
    
    d = d[d[q] > .5] #pick out the subset of responses with non-zero entries for question q      
    #matched = F.match_subset(d)
    #d = F.data_query(d,SID = matched)
    #print len(d)
#    print d[q] > .5
#    r=q.replace('a','b')        
    ind=np.arange(5)
    fig=py.figure(figsize=figsize)
    gs=gridspec.GridSpec(1,1)
    ax=fig.add_subplot(gs[0])
    
    pre_list = F.data_query(d,PrePost='Pre')[q]
    post_list = F.data_query(d,PrePost='Post')[q]
#    print "pre_list = {}".format(len(pre_list))
#    print "post_list = {}".format(len(post_list))
    if q=='q30c':
        pre_list = pre_list.apply(np.float)            
    hist_data, data_err = F.hist_process_data(pre_list,scaled=False)
    hist1= F.hist_with_err(ax,hist_data,data_err,width,data_series_num=1,ind=ind,colour=_color1)

    
#    practice_list = basic.data_subset_modified(d,PrePost='Post')[r]
    if q=='q30c':
        post_list=post_list.apply(np.float)
    hist_data, data_err = F.hist_process_data(post_list,scaled=False)
    hist2= F.hist_with_err(ax,hist_data,data_err,width,data_series_num=0,ind=ind,colour=_color2)
    #hist2 = F.hist(ax,post_list,width,1,ind,_color2)
#    corr = pearsonr(pre_list,post_list)
    
    total_num = len(pre_list)
    title = F.header_post[q][0]+' ' + F.header_post[q][1]+ ' N='+str(total_num)#+' r='+str(corr)
    py.title(wrap_text2(title,50),fontsize=axes_label_fontsize) 
    py.xticks(np.arange(1,6)-width,['Strongly\nDisagree', 'Disagree', 'Neutral','Agree','Strongly\nAgree'],\
        fontsize=axes_label_fontsize,rotation=45,horizontalalignment='right') 
    py.ylabel('Number of Students',fontsize=axes_label_fontsize)
    lgd=ax.legend((hist1[0],hist2[0]),('pre','post'),loc=3,bbox_to_anchor = (0., 1.02, 1., .102),prop={"size":12})
    ymin, ymax = py.ylim()
    py.ylim(0,ymax)
    py.xlim(1 - 3*width, 5+0.5*width)
    py.tight_layout()
    py.subplots_adjust(right=.75)
    lgd=ax.legend((hist1[0],hist2[0]),('Pre','Post'),loc=10,bbox_to_anchor = (.7, .5, 1., .102),prop={"size":12})
    if save_fig == True :         
        fig.savefig(save_directory+"Single_Question_Interleaved_pre_post_Hist.png",dpi=300)         
#        fig.savefig(save_directory+"Single_Question_Interleaved_pre_post_Hist.png",bbox_extra_artists=(lgd,),bbox_inches='tight',dpi=300)
        py.close()
    return
    
def gains_1D_compare2(datain1,datain2,datain1_name,datain2_name,save_fig=False,\
            sortby='pre',qtype='personal', exp_nonexp='expertlike', save_directory='empty'):
    """
    This function assumes the user selects the subset of courses prior to calling
    the gains_1D_categories function

    datain1 should be the same data set as datain2 (lazy coding to keep it in there)

    "savefigs" will save a high res PNG and a PDF of the figure when set to True.

    "sortby" can take on values 'pre', 'post', or 'shift'.  THe sorting
    starts with most positive at the top, and least positive at the bottom.

    "qtype" should be 'personal', 'professional', 'grade', 'practice'

    "exp_nonexp" lets user choose whether expertlike ('expertlike') or non-expertlike ('nonexpertlike' fractions
    are plotted.
    It is really a matter of whether the data is projected on the expertlike or
    non-expertlike axis.

    """

    #make the q_list ordered right off the bat from most expertlike to least expert like
    #d1 = F.data_query(datain1,q40a=4,q40b=4)  #pick only students who answered the test questions
    #d2 = F.data_query(datain2,q40a=4,q40b=4)  #pick only students who answered the test questions

    q_list = F.get_q_list(qtype)  #Make a list of all the question names of this type.
    data1_all_questions = gains_1D_process_data(datain1,qtype=qtype,q_list=q_list)
#    print data_1_all_questions
    df = data1_all_questions


    num_match_series_all_questions= df['pre_expert']+df['pre_nonexpert']+df['pre_neutral']

#    print num_match_series_all_questions
    sortby_series = 1.0*df['pre_expert']/num_match_series_all_questions
#    print sortby_series
    sortby_series.sort()
#    print sortby_series
    exp_dict = {}
    for q in q_list:
        exp_dict[q]=F.change_q_type(q,qtype) #for All_basic, change_q_type has changed
    sortby_series2=sortby_series.rename(exp_dict)
    #print "exp_dict = {}".format(exp_dict)
#    sortby_series = sortby_series[::-1]
    q_list = sortby_series.index

    #split up questions across two pages...
    q_list1 = q_list[0:14]
    q_list2 = q_list[15:29]
    q_list_total = [q_list1,q_list2]

    counter_plot_num = 1

    for q_list_num in range(len(q_list_total)):
        fig_size = (7,8)
        gridspec_width_ratio = [1,2]
        fig = py.figure(figsize=fig_size)
        gs = gridspec.GridSpec(1, 2,width_ratios=gridspec_width_ratio)
        ax = fig.add_subplot(gs[0])
        #ax = fig.add_subplot(121)
        ax.set_xlim(0,1)

        #Add vertical grid lines
        ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')
    #    offset = 0.2
        q_list_now = q_list_total[q_list_num]

        d1 = F.data_query(datain1,q40a=4,q40b=4)  #pick only students who answered the test questions
        d1.ix[q_list_now]
        data1 = gains_1D_process_data(d1,qtype=qtype,q_list=q_list_now)
        #print "data1 = {}".format(data1)

        d2 = F.data_query(datain2,q40a=4,q40b=4)  #pick only students who answered the test questions
        d2.ix[q_list_now]
        data2 = gains_1D_process_data(d2,qtype=qtype,q_list=q_list_now)
        #print "data2 = {}".format(data2)


        #do the sorting (assuming 'pre')
        df = data1
        num_match_series= df['pre_expert']+df['pre_nonexpert']+df['pre_neutral']
        sortby_series = 1.0*df['pre_expert']/num_match_series
        sortby_series2=sortby_series.rename(exp_dict)
        #print "sortby_series = {}".format(sortby_series)
        #print "sortby_series2 = {}".format(sortby_series2)

        dax,lgd=plot_gains_1D_v3(ax,data2, sortby_series2, \
                    offset=-.2, colour='b', exp_nonexp='expertlike', qtype=qtype, categories=False, \
                    plot_title=False, text_labels=False,show_legend=True,legend_label=datain2_name)
        eax,lgd=plot_gains_1D_v3(dax,data1, sortby_series, \
                    offset=.2, colour='r', exp_nonexp='expertlike', qtype=qtype, categories=False, \
                    plot_title=False, text_labels=True,show_legend=True,legend_label=datain1_name)

    #    ax.legend([circ1,circ2],[datain1_name,datain2_name],bbox_to_anchor=(.01,1),loc=2)
        py.suptitle('What do YOU think?',fontweight='bold')

        #py.tight_layout()
        py.subplots_adjust(top=0.9)

        if save_fig == True :
            filename = "All_Questions_pre_post_change" + str(counter_plot_num) + ".PNG"
            py.savefig(save_directory + filename,dpi=300)
#            py.savefig(save_directory + filename,bbox_extra_artists=(lgd,),bbox_inches='tight',dpi=300)
#            filename = datain1_name+"_vs_"+ datain2_name +"_gains_1D" +str(q_list_num)+ ".PDF"
#            py.savefig(save_directory + filename)
        counter_plot_num += 1


def gains_1D_compare_personal_professional(datain1,datain2,datain1_name,datain2_name,save_fig=False,\
            sortby='pre',qtype1='personal',qtype2='professional',exp_nonexp='expertlike', save_directory='empty'):
    """
    This function assumes the user selects the subset of courses prior to calling
    the gains_1D_categories function
    
    datain1 should be the same data set as datain2 (lazy coding to keep it in there)
    
    "savefigs" will save a high res PNG and a PDF of the figure when set to True.
    
    "sortby" can take on values 'pre', 'post', or 'shift'.  THe sorting
    starts with most positive at the top, and least positive at the bottom.
    
    "qtype" should be 'personal', 'professional', 'grade', 'practice'
    
    "exp_nonexp" lets user choose whether expertlike ('expertlike') or non-expertlike ('nonexpertlike' fractions 
    are plotted. 
    It is really a matter of whether the data is projected on the expertlike or 
    non-expertlike axis.
    
    """
    
    #make the q_list ordered right off the bat from most expertlike to least expert like
    #d1 = F.data_query(datain1,q40a=4,q40b=4)  #pick only students who answered the test questions
    #d2 = F.data_query(datain2,q40a=4,q40b=4)  #pick only students who answered the test questions
    
    q_list = F.get_q_list(qtype1)  #Make a list of all the question names of this type.     
    data1_all_questions = gains_1D_process_data(datain1,qtype=qtype1,q_list=q_list)
#    print data_1_all_questions
    df = data1_all_questions


    num_match_series_all_questions= df['pre_expert']+df['pre_nonexpert']+df['pre_neutral']
    
#    print num_match_series_all_questions
    sortby_series = 1.0*df['pre_expert']/num_match_series_all_questions
#    print sortby_series
    sortby_series.sort()
#    print sortby_series
    exp_dict = {}
    for q in q_list:
        exp_dict[q]=F.change_q_type(q,qtype2) #for All_basic, change_q_type has changed
    sortby_series2=sortby_series.rename(exp_dict)
    #print "exp_dict = {}".format(exp_dict)
#    sortby_series = sortby_series[::-1]
    q_list = sortby_series.index
       
    #split up questions across two pages...
    q_list1 = q_list[0:14]
    q_list2 = q_list[15:29]
    q_list_total = [q_list1,q_list2]
    
    counter_plot_num = 1
    
    for q_list_num in range(len(q_list_total)):
        fig_size = (7,8)
        gridspec_width_ratio = [1,2] 
        fig = py.figure(figsize=fig_size)
        gs = gridspec.GridSpec(1, 2,width_ratios=gridspec_width_ratio)
        ax = fig.add_subplot(gs[0])
        #ax = fig.add_subplot(121)    
        ax.set_xlim(0,1)  
        
        #Add vertical grid lines    
        ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')    
    #    offset = 0.2    
        q_list_now = q_list_total[q_list_num]
        q_list_now2 = []
        for q in q_list_now :
            q_list_now2.append(q.replace('a','b'))
        
        
        d1 = F.data_query(datain1,q40a=4,q40b=4)  #pick only students who answered the test questions
        d1.ix[q_list_now]
        data1 = gains_1D_process_data(d1,qtype=qtype1,q_list=q_list_now)
        #print "data1 = {}".format(data1)

        d2 = F.data_query(datain2,q40a=4,q40b=4)  #pick only students who answered the test questions
        d2.ix[q_list_now2]
        data2 = gains_1D_process_data(d2,qtype=qtype2,q_list=q_list_now2)
        #print "data2 = {}".format(data2)

        
        #do the sorting (assuming 'pre')
        df = data1
        num_match_series= df['pre_expert']+df['pre_nonexpert']+df['pre_neutral']    
        sortby_series = 1.0*df['pre_expert']/num_match_series
        sortby_series2=sortby_series.rename(exp_dict)
        #print "sortby_series = {}".format(sortby_series)
        #print "sortby_series2 = {}".format(sortby_series2)

        dax,lgd=plot_gains_1D_v3(ax,data2, sortby_series2, \
                    offset=-.2, colour='g', exp_nonexp='expertlike', qtype='professional', categories=False, \
                    plot_title=False, text_labels=False,show_legend=True,legend_label='Physicists')
        eax,lgd=plot_gains_1D_v3(dax,data1, sortby_series, \
                    offset=.2, colour='r', exp_nonexp='expertlike', qtype='personal', categories=False, \
                    plot_title=False, text_labels=True,show_legend=True,legend_label='You')

    #    ax.legend([circ1,circ2],[datain1_name,datain2_name],bbox_to_anchor=(.01,1),loc=2)
        py.suptitle('What do YOU think? and\nWhat would experimental physicists say about their research?',fontweight='bold')
        
        #py.tight_layout()
        py.subplots_adjust(top=0.9)
        
        if save_fig == True :         
            filename = "All_Questions_you_vs_physicist_split_" + str(counter_plot_num) + ".PNG"
            py.savefig(save_directory + filename,dpi=300)
#            py.savefig(save_directory + filename,bbox_extra_artists=(lgd,),bbox_inches='tight',dpi=300)
#            filename = datain1_name+"_vs_"+ datain2_name +"_gains_1D" +str(q_list_num)+ ".PDF"
#            py.savefig(save_directory + filename)
        counter_plot_num += 1


def plot_gains_1D_v3(ax,pre_shift_dataframe, sortby, offset,colour='r', \
                  exp_nonexp='expertlike', qtype='personal', categories=False, \
                  plot_title = True, text_labels = True,show_legend=False, legend_label='none') :
    """
    Generate the 1D bar chart plot for a set of questions or categories
    If sortby = 'pre', 'post', or 'shift' then sort the datasets given in the function.
    If sortby is a pandas.Series object, then sort by that series.
    """    
    
    pre_expert_series = pre_shift_dataframe['pre_expert']
    shift_expert_series = pre_shift_dataframe['shift_expert']
    pre_nonexpert_series = pre_shift_dataframe['pre_nonexpert']
    shift_nonexpert_series = pre_shift_dataframe['shift_nonexpert']
    pre_neutral_series = pre_shift_dataframe['pre_neutral']
    
    
    num_matched_series = pre_expert_series + pre_neutral_series + pre_nonexpert_series
    
    if exp_nonexp == 'expertlike' :
        pre_series = pre_expert_series
        shift_series = shift_expert_series
    elif exp_nonexp == 'nonexpertlike':
        pre_series = pre_nonexpert_series
        shift_series = shift_nonexpert_series
    else :
#        print "exp_nonexp set to invalid value.  Should be 'expertlike' or 'nonexpertlike'"
#        print "Method failed."
        return -1 

    #sort by the normalized responses (not total because num_matched can vary for different categories)        
    if isinstance(sortby,p.Series) :
        sort_series = sortby    
    elif sortby == 'pre' :
        sort_series = 1.0*pre_series/num_matched_series
    elif sortby == 'shift' :
        sort_series = 1.0*shift_series/num_matched_series
    elif sortby == 'post' :
        sort_series = 1.0*(pre_series + shift_series)/num_matched_series
    else :  #default is to sort by 'pre'
        sort_series = 1.0*pre_series/num_matched_series
    
    sort_series.sort()
#    print sort_series

    ax.set_ylim(.5,len(pre_series) + .5) #There are 30 questions
#    
#    #Add vertical grid lines    
#    ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')

    q_last = sort_series.index[-1]  #pick out the last question to get a plot legend label
    #loop over all the questions and make the plot
    counter = 1
    for q in sort_series.index :
#        num_matched = pre_expert_series[q] + pre_neutral_series[q] + pre_nonexpert_series[q]
        pre_norm = pre_series[q]*1.0/num_matched_series[q]
        shift_norm = shift_series[q]*1.0/num_matched_series[q]
#        print q + ", N = " + str(num_matched_series[q]) + ", pre_norm = " + str(pre_norm) + ", shift_norm = " + str(shift_norm)

        #plot the horizontal grid line        
        ax.plot([0,1],[counter,counter], '--', color='0.8')
        #plot the marker at the pre position 
        if q == q_last:
            ax.plot([pre_norm], [counter+offset], 'o',color=colour,label=legend_label)
        else:
            ax.plot([pre_norm], [counter+offset], 'o',color=colour)                
        #ax.plot([pre_norm], [counter+offset], 'o',color=colour)
        #plot the arrow if there is a nonzero shift        
        if shift_norm != 0.0 :        
            ax.arrow(pre_norm, counter+offset, shift_norm, 0, \
                     length_includes_head = True, head_width = 0.3, head_length = 0.03, facecolor=colour)
#        print "Pre_expert = " + str(pre_expert_series[q]) + "  Pre_nonexpert = " + str(pre_nonexpert_series[q]) + " num_matched = " + str(num_matched)
        #calculate the error bars on the pre-value        
        if exp_nonexp == 'expertlike' :
            pre_expert_series
#        print "fav_act = " + str(pre_expert_series[q]) + ", unfav_act = " + str(pre_nonexpert_series[q]) + ", num_matched = " + str(num_matched_series[q])
        expert_unc, nonexpert_unc = F.uncertainty_1D_fast(fav_act=pre_expert_series[q], \
                    unfav_act=pre_nonexpert_series[q], num_matched=num_matched_series[q])
#        print "expert_unc = " + str(expert_unc) + ", nonexpert_unc = " + str(nonexpert_unc)
        
        #Pick the correct uncertainty depending on whether expertlike or nonexpertlike is chosed        
        if exp_nonexp == 'expertlike' :
            uncertainty = expert_unc
        elif exp_nonexp == 'nonexpertlike' :
            uncertainty = nonexpert_unc
        
        uncertainty_norm = uncertainty/num_matched_series[q]
        
        sigma_scale = 1.95996 #gives the 95% confidence interval
        uncertainty_norm *= sigma_scale #scale uncertainty to a 95% confidence interval
        #print "expert_unc = " + str(expert_unc)
        #plot the error interval        
#        print "This is where it makes the error bar"  +str([[pre_norm - uncertainty_norm, pre_norm + uncertainty_norm],
#                [counter, counter]])      
        ax.plot([pre_norm - uncertainty_norm, pre_norm + uncertainty_norm], \
                [counter+offset, counter+offset],color=colour,lw=8,alpha=0.2 )        
        
        #Add the question text
        #title = str(pre_expert_series[q])+ ", "+ str(pre_nonexpert_series[q]) + "  " + header_pre[q][0]
        if categories == False :        
            title = F.header_pre[q]['Question Text']        
        elif categories == True :
            title = q + ", N = " + str(num_matched_series[q]) #This is just the category name
        
        if text_labels == True :
            title = wrap_text2(title,line_len=65)            
            ax.text(1.02, counter, title,fontsize=fontsize_1D_question_text,verticalalignment='center')
        
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(tickfontsize)
            tick.label1.set_visible(False)        
        
        counter = counter + 1
    if show_legend == True:
        lgd=ax.legend(loc=2,fontsize='10',ncol=2,bbox_to_anchor = (-0.045,1.05))
    if exp_nonexp == 'expertlike' :    
        py.xlabel('Fraction of class with expert-like response',x = 0, y = -1, fontsize=axes_label_fontsize,horizontalalignment='left')
    elif exp_nonexp == 'nonexpertlike' :    
        py.xlabel('Fraction of class with nonexpert-like response',fontsize=axes_label_fontsize,horizontalalignment='left')

    py.subplots_adjust(bottom=0.08, left=.04, right=.99, top=.92, hspace=.1)
    if plot_title == True:
        if qtype == 'personal' :
            qtext = 'What do YOU think?'
        elif qtype == 'professional' :
            qtext = 'What would experimental physicists say about their research?'
        elif qtype == 'grade' :
            qtext = 'How important was this for earning a good grade?'
        elif qtype == 'practice' :
            qtext = 'How often did you engage in this practice?'
        py.suptitle(qtext +  '  N = '+str(num_matched_series[q]) + ", Showing " + exp_nonexp + " responses, sorting by " + sortby, )
    #py.show()
    if show_legend == True:
        return ax, lgd
    else:
        return ax

def gains_1D_process_data(data_in,q_list,qtype='personal',for_categories=False) :
    '''
    Given an input data set, returns a dataframe with columns:
    pre_expert_series
    shift_expert_series 
    pre_nonexpert_series 
    shift_nonexpert_series
    pre_neutral_series 
    '''
   
    #Build a series of pre scores and shifts
    pre_expert_dict = {}  #dictionaries indexed by the question number
    pre_nonexpert_dict = {} #need this to compute uncertainty intervals
    pre_neutral_dict = {} #need this to compute uncertainty intervals
    shift_expert_dict = {}
    shift_nonexpert_dict = {} #Need this only to give flexibility in sorting
    shift_neutral_dict = {}# .
    for q in q_list:
#        print q
        #The code is so fast now, that a status update is not necessary.
        #if q in ['q10a', 'q20a', 'q30a']:        
            #print q  #give a status update
        #select out a matched subset of valid responses        
        d = F.data_query(data_in, q40a=4,q40b=4)  #pick only students who answered the test questions

        #print q
        d = d[d[q] > 0] #Pick out subset of responses that are non-zero for this particular question       
        preresponses = F.data_query(d,PrePost='Pre')
        postresponses = F.data_query(d,PrePost='Post')
        #matched = F.match_subset(d)
        #num_matched = len(matched)
        #print "num_matched = {}".format(num_matched)
        #preresponses_matched = F.data_query(preresponses, SID=matched)
        #postresponses_matched = F.data_query(postresponses, SID=matched)
        
        #pre_dist = preresponses_matched[q].value_counts()  #value_counts gives the number of each response
        pre_dist = preresponses[q].value_counts()  #value_counts gives the number of each response
        #print "pre_dist = {}".format(pre_dist)

        #post_dist = postresponses_matched[q].value_counts()
        post_dist = postresponses[q].value_counts()
        #print post_dist

        #Clean up the pre_dist and post_dist        
        for i in range(1,6):
            if not (i in pre_dist.index) :
                pre_dist = pre_dist.append(p.Series({i:0}))    
            if not (i in post_dist.index) :
                post_dist = post_dist.append(p.Series({i:0}))
        #print pre_dist
        #print post_dist
                
        #if question has a disagree expert response, negate the answers
        if F.header_pre[q][3] == 'n': 
            pre_expert_dict[q] = pre_dist[1]+pre_dist[2] #All 1's and 2's are expert-like
            post_expert = post_dist[1]+post_dist[2]
            pre_nonexpert_dict[q] = pre_dist[4]+pre_dist[5] #All 4's and 5's are non-expertlike
            post_nonexpert = post_dist[4]+post_dist[4]
        else :
            pre_expert_dict[q] = pre_dist[5]+pre_dist[4]  #All 4's and 5's are expertlike
            post_expert = post_dist[5]+post_dist[4]
            pre_nonexpert_dict[q] = pre_dist[1]+pre_dist[2] # All 1's and 2's are nonexpertlike
            post_nonexpert = post_dist[1]+post_dist[2]
        pre_neutral_dict[q] = pre_dist[3]
        post_neutral = post_dist[3]
        
        shift_expert_dict[q] = post_expert - pre_expert_dict[q]
        shift_neutral_dict[q] = post_neutral - pre_neutral_dict[q]
        shift_nonexpert_dict[q] = post_nonexpert - pre_nonexpert_dict[q]
    
    
    #convert the dictionaries into Pandas Series type
    pre_expert_series = p.Series(pre_expert_dict)
    shift_expert_series = p.Series(shift_expert_dict)
    pre_nonexpert_series = p.Series(pre_nonexpert_dict)
    shift_nonexpert_series = p.Series(shift_nonexpert_dict)
    pre_neutral_series = p.Series(pre_neutral_dict)
    shift_neutral_series = p.Series(shift_neutral_dict)
    dataframe_dict = {'pre_expert':pre_expert_series, \
                    'shift_expert':shift_expert_series, \
                    'pre_nonexpert':pre_nonexpert_series, \
                    'shift_nonexpert':shift_nonexpert_series,\
                    'pre_neutral':pre_neutral_series,\
                    'shift_neutral':shift_neutral_series}

    if for_categories == True:
        #Create a pre_series and a shift series for all the categories
        pre_expert_dict_cat = {}
        pre_neutral_dict_cat = {}
        pre_nonexpert_dict_cat = {}
        shift_expert_dict_cat = {}    
    #    shift_neutral_dict_cat = {}
        shift_nonexpert_dict_cat = {}
    
        cat_list = F.get_categories()
        for cat in cat_list :
            q_cat = F.get_q_list(qtype=qtype, category=cat)
            pre_expert_dict_cat[cat] = pre_expert_series[q_cat].sum()
            shift_expert_dict_cat[cat] = shift_expert_series[q_cat].sum()
            pre_nonexpert_dict_cat[cat] = pre_nonexpert_series[q_cat].sum()
            shift_nonexpert_dict_cat[cat] = shift_nonexpert_series[q_cat].sum()
            pre_neutral_dict_cat[cat] = pre_neutral_series[q_cat].sum()
        pre_expert_series_cat = p.Series(pre_expert_dict_cat)
        shift_expert_series_cat = p.Series(shift_expert_dict_cat)
        pre_nonexpert_series_cat = p.Series(pre_nonexpert_dict_cat)
        shift_nonexpert_series_cat = p.Series(shift_nonexpert_dict_cat)
        pre_neutral_series_cat = p.Series(pre_neutral_dict_cat)    
        dataframe_dict = {'pre_expert_cat':pre_expert_series_cat, \
                        'shift_expert_cat':shift_expert_series_cat,\
                        'pre_nonexpert_cat':pre_nonexpert_series_cat,\
                        'shift_nonexpert_cat':shift_nonexpert_series_cat,\
                        'pre_neutral_cat':pre_neutral_series_cat}
               
    return p.DataFrame(dataframe_dict)

def plot_scatter_shift_and_pre_vs_grade(data_class,save_fig=False, save_directory='empty'):
    
    q_list_personal = F.get_q_list(qtype='personal')  #get list of all "personal" questions
    #d = F.data_subset(Class=course,q40a=4, q40b=4)  #pick out data from course of interest
    d = data_class
    pre_shift_df = gains_1D_process_data(data_in=d,q_list=q_list_personal,qtype='personal',for_categories=False)
    #make a series of the total number of responses to normalize the shift    
    num_matched_series = pre_shift_df['pre_expert'] + pre_shift_df['pre_neutral'] + pre_shift_df['pre_nonexpert']
    shift_fraction_series = 1.0*pre_shift_df['shift_expert']/num_matched_series
    
    pre_fraction_series = 1.0*pre_shift_df['pre_expert']/num_matched_series    
    
    #Get the grade data
    #matched_IDs = F.match_subset_str(d)  #Matching is irrelevant with new routine because data is already matched.
    #d_matched = F.data_subset_modified(d, SID=matched_IDs)
    grade_df = make_grade_table(data_class=d,data_level=d)
    grade_series = grade_df['Mean (Class)']
    
    num_matched = len(d)/2
    
    fig = py.figure(figsize=(4.5,4.))
    ax=py.subplot(111)
    ax.plot([0,5],[0,0],'k--',alpha=0.2)
    
    fig2 = py.figure(figsize=(4.5,4.))
    ax2=py.subplot(111)
    ax2.plot([0,5],[0,0],'k--',alpha=0.2)
#    ax.plot([0,0],[-4,4],'k--',alpha=0.2)
    
    x_list = []  #grade
    y_list = []  #shift
    y2_list = [] #pre
    
    for q in grade_series.index :
        x = grade_series[q]
        q_personal = q.replace('c','a')
        y = shift_fraction_series[q_personal]
        y2 = pre_fraction_series[q_personal]
        #Is this flip of sign bogus?
        x = x - 1 #shift so x = 0 means totally unimportant        
        if F.header_post[q][3] == 'n':        
            x = -x  #a negative importance for grade means encouraging bad habits...
            continue  #skip the plotting if the point is negative
        
        alpha = 0.4        
        ax.plot(x,y,'o', alpha=alpha)
        ax2.plot(x,y2,'o', alpha=alpha)
        qlabel=q[1:3] #drop the initial 'q' and the final 'c' from the question ID
        qlabel=qlabel.lstrip('0')  #strip off the leading zero if it exists
        ax.annotate(qlabel,xy=(x+0.06,y),verticalalignment='center',fontsize=10)
        ax2.annotate(qlabel,xy=(x+0.06,y2),verticalalignment='center',fontsize=10)
        x_list.append(x)
        y_list.append(y)
        y2_list.append(y2)
       
    
    ylim = max([abs(max(y_list)), abs(min(y_list))])
    ax.set_ylim(-1.1*ylim,1.1*ylim)
    ax2.set_ylim(0,1.1)

    ax.set_xlim(0,4)
    ax2.set_xlim(0,4)
    ax.set_xticks([0,1,2,3,4])
    ax.set_xticklabels(['Unimportant','','','','Very Important'], fontsize = axes_label_fontsize)    
    ax2.set_xticks([0,1,2,3,4])
    ax2.set_xticklabels(['Unimportant','','','','Very Important'],fontsize = axes_label_fontsize)    
    
    ax.set_yticklabels(ax.get_yticks(),fontsize = axes_label_fontsize) 
    ax2.set_yticklabels(ax2.get_yticks(),fontsize = axes_label_fontsize)    
    
    corr = stats.pearsonr(x_list,y_list)
    corr2 = stats.pearsonr(x_list,y2_list)
    
    ax.set_xlabel('Mean Importance for earning a good grade', fontsize = axes_label_fontsize)
    ax.set_ylabel(wrap_text2('Change in fraction of class with expert-like response', 35),\
        multialignment='center', fontsize = axes_label_fontsize)
    ax.set_title('N = {}, Correlation = {:.3f}'.format(num_matched, corr[0]),fontsize=12)
    ax2.set_xlabel('Mean Importance for earning a good grade',fontsize = axes_label_fontsize)
    ax2.set_ylabel(wrap_text2('Fraction of class with expert-like response (Pre)', 35),\
        multialignment='center', fontsize = axes_label_fontsize)
    ax2.set_title('N = {}, Correlation = {:.3f}'.format(num_matched, corr2[0]),fontsize=12)    
    ax.set_aspect(aspect=4/(2*1.1*ylim))
    ax2.set_aspect(aspect=4/(1.1))    
    fig.tight_layout()
    fig2.tight_layout()
    
    if save_fig == True:
        filename = "Shift_vs_Grade_Scatterplot.PNG"
        filename2 = "Pre_vs_Grade_Scatterplot.PNG"
        fig.savefig(save_directory+filename,dpi=300)
        fig2.savefig(save_directory+filename2,dpi=300)
 
def get_course_level(course):
    #Get the row of data for the course of interest
    course_level=F.data_subset_modified(F.course_data,Instructor_html=course)  
    course_level=course_level['Alg_Calc_Other_Letter']  #get the letter
#    print course_level.values[0]
    course_list = F.course_query(Alg_Calc_Other_Letter=course_level.values[0])
    if course_list == 'A':
        course_level_name = 'non-calc intro'
    elif course_list == 'C':
        course_level_name = 'calc intro'
    else:
        course_level_name = 'upper div'
    course_list_total = [course, course_list]
    names = [course,course_level_name]
    return course_list_total, names

def make_grade_table(data_class,data_level):
    class_table = F.course_goals(data_class)
    level_table = F.course_goals(data_level)
    #rename the columns to indicate course or level
    class_table.columns = ['Question_Text', 'Mean (Class)', 'SD (Class)']
    level_table.columns = ['Question_Text','Mean (Level)', 'SD (Level)']
    #concatenate into one grade table.
    combo_table = F.p.concat([class_table,level_table[['Mean (Level)','SD (Level)']]],axis=1)
    combo_table = combo_table.sort('Mean (Class)', ascending=False)
    combo_table['Mean (Class)'] = combo_table['Mean (Class)'].round(decimals = 2)
    combo_table['SD (Class)'] = combo_table['SD (Class)'].round(decimals = 2)
    combo_table['Mean (Level)'] = combo_table['Mean (Level)'].round(decimals = 2)
    combo_table['SD (Level)'] = combo_table['SD (Level)'].round(decimals = 2)

    return combo_table

def plot_grade_table(data_class,data_level,save_fig=False, save_directory='empty') :
    combo_table = make_grade_table(data_class,data_level)
    combo_table = combo_table.sort('Mean (Class)', ascending=True)
    fig_size = (7,7)
    gridspec_width_ratio = [1.5,2]

    plot_sections_index = [combo_table['Mean (Class)'].index[0:12],\
           combo_table['Mean (Class)'].index[12:23]]

    for i in range(0,2) :
        q_index = plot_sections_index[i]

        fig = py.figure(figsize=fig_size)
        gs = gridspec.GridSpec(1, 2,width_ratios=gridspec_width_ratio)
        ax = fig.add_subplot(gs[0])
        #ax = fig.add_subplot(121)
        ax.set_xlim(1,5)

        #Add vertical grid lines
        ax.grid(axis='x', color=(.5,.5,.5,.1), lw=1, linestyle=':')

        course_color = 'r'
        level_color = 'b'
        course_offset = 0.2
        level_offset = -0.2

        counter = 1
        q_last = q_index[-1]  #pick out the last question to get a plot legend label

        #for q in combo_table['Mean (Class)'].index :
        for q in q_index :

            course_Mean = combo_table['Mean (Class)'][q]
            course_SD = combo_table['SD (Class)'][q]
            level_Mean = combo_table['Mean (Level)'][q]
            level_SD = combo_table['SD (Level)'][q]


            #plot the horizontal grid line
            ax.plot([1,5],[counter,counter], '--', color='0.8')
            #plot the marker at the pre position
            if q == q_last:
                ax.plot([course_Mean], [counter+course_offset], 'o',color=course_color,\
                        label=_legend_label_class)
                ax.plot([level_Mean], [counter+level_offset], 'o',color=level_color,\
                        label=_legend_label_level)
            else:
                ax.plot([course_Mean], [counter+course_offset], 'o',color=course_color)
                ax.plot([level_Mean], [counter+level_offset], 'o',color=level_color)
            #ax.plot([pre_norm], [counter+offset], 'o',color=colour)

            #plot the error interval
    #        print "This is where it makes the error bar"  +str([[pre_norm - uncertainty_norm, pre_norm + uncertainty_norm],
    #                [counter, counter]])
            ax.plot([course_Mean - course_SD, course_Mean + course_SD], \
                    [counter+course_offset, counter+course_offset],\
                    color=course_color,lw=8,alpha=0.2 )
            ax.plot([level_Mean - level_SD, level_Mean + level_SD], \
                    [counter+level_offset, counter+level_offset],\
                    color=level_color,lw=8,alpha=0.2 )

            #Add the question text

            q_text = combo_table['Question_Text'][q]
            q_text = wrap_text2(q_text,line_len=58)
            ax.text(5.1, counter, q_text,fontsize=11,verticalalignment='center')

            for tick in ax.yaxis.get_major_ticks():
                tick.label1.set_fontsize(tickfontsize)
                tick.label1.set_visible(False)
            counter += 1

        ax.set_ylim(0.5,counter-0.5)
        title = "How important for earning a good grade in this class was..."
        py.suptitle(title,fontweight='bold')
        py.xticks([1,2,3,4,5],['Un-\nimportant', '', '','','Very\nImportant'],\
            fontsize=axes_label_fontsize,horizontalalignment='center')
        lgd=ax.legend(loc=3,fontsize='10',ncol=2,bbox_to_anchor = (0,1.01),borderaxespad=0.)
        py.subplots_adjust(left=0.07,top=0.90, bottom=0.07)

        if save_fig == True :
            filename = "Importance_for_grade_plot_" + str(i) + ".PNG"
            py.savefig(save_directory + filename,dpi=300)
    return combo_table
