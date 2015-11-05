
import pandas

def get_counts_from_raw_data(pre : pandas.DataFrame, post: pandas.DataFrame, matched : pandas.DataFrame, course_id : str):
    """
    gets counts of participating students in pre-survey,
    post survey, and the matched count.
    """
    pre_count = pre.ix[course_id]
    post_count = post.ix[course_id]
    matched_count = matched.ix[course_id]
    return pre_count, post_count, matched_count

def get_reported_student_count(df : pandas.DataFrame, course_id : str):
    """
    returns reported count of students who will participate
    """
    return df.ix[course_id]

def fraction_of_participating_students(matched_count : int, reported_count : int):
    """
    calculates the fraction of students who participated out of those 
    who were reported would be participating
    """
    return float(matched_count)/float(reported_count)

def table_one_data(valid_pre : int, valid_post : int, valid_matched : int, reported_student_count : int, participating_student_fraction : float):
    """
    contructs a zip generator that returns the data for table one
    """
    table_one_text = ['Number of valid pre-responses', 'Number of valid post-responses', 'Number of matched responses', 'Reported number of students in class', 'Fraction of class participating in pre and post']
    return zip(table_one_text, [valid_pre, valid_post, valid_matched, reported_student_count, participating_student_fraction])