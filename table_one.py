
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