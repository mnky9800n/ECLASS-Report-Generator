
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
        # TODO : Delete this block, save for posterity (it's the only place with a complete question text)
        #self.questionIDToQuestionText = [('q01a', 'When doing an experiment, I try to understand how the experimental setup works. What do YOU think?')
        #                            ,('q01b', 'When doing an experiment, I try to understand how the experimental setup works. What would an experimental physicist say about their research?')
        #                            ,('q01c', 'How important for earning a good grade in this class was understanding how the experimental setup works?')
        #                            ,('q02a', "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment. What do YOU think?")
        #                            ,("q02b", "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment. What would an experimental physicist say about their research?")
        #                            ,("q02c", "How important for earning a good grade in this class was understanding how the measurement tools and sensors work?")
        #                            ,("q03a", "When doing a physics experiment, I don't think much about sources of systematic error. What do YOU think?")
        #                            ,("q03b", "When doing a physics experiment, I don't think much about sources of systematic error. What would an experimental physicist say about their research?")
        #                            ,("q03c", "How important for earning a good grade in this class was thinking about sources of systematic error?")
        #                            ,("q04a", "It is helpful to understand the approximations and simplifications that go into the theoretical predictions when comparing them with data. What do YOU think?")
        #                            ,("q04b", "It is helpful to understand the approximations and simplifications that go into the theoretical predictions when comparing them with data. What would an experimental physicist say about their research?")
        #                            ,("q04c", "How important for earning a good grade in this class was understanding the approximations and simplifications that are included in theoretical predictions?")
        #                            ,("q05a", "Whenever I use a new measurement tool, I try to understand its performance limitations. What do YOU think?")
        #                            ,("q05b", "Whenever I use a new measurement tool, I try to understand its performance limitations. What would an experimental physicist say about their research?")
        #                            ,("q05c", "How important for earning a good grade in this class was understanding the performance limitations of the measurement tools?")
        #                            ,("q06a", "Doing error analysis (such as calculating the propagated error) usually helps me understand my results better. What do YOU think?")
        #                            ,("q06b", "Doing error analysis (such as calculating the propagated error) usually helps me understand my results better.  What would an experimental physicist say about their research?")
        #                            ,("q06c", "How important for earning a good grade in this class was using error analysis (such as calculating the propagated error) to better understand my results?")
        #                            ,("q07a", "If the lab guide doesn't give clear directions for analyzing data, I am not sure how to choose an appropriate method to analyze my data. What do YOU think?")
        #                            ,("q07b", "If the lab guide doesn't give clear directions for analyzing data, I am not sure how to choose an appropriate method to analyze my data. What would an experimental physicist say about their research?")
        #                            ,("q07c", "How important for earning a good grade in this class was choosing an appropriate method for analyzing data (without explicit direction)?")
        #                            ,("q09a", "I am usually able to complete an experiment without understanding the equations and physics ideas that describe the system I am investigating. What do YOU think?")
        #                            ,("q09b", "I am usually able to complete an experiment without understanding the equations and physics ideas that describe the system I am investigating. What would an experimental physicist say about their research?")
        #                            ,("q09c", "How important for earning a good grade in this class was understanding the equations and physics ideas that describe the system I am investigating?")
        #                            ,("q10a", "I try to understand the theoretical equations provided in the lab guide. What do YOU think?")
        #                            ,("q10b", "I try to understand the theoretical equations provided in the lab guide. What would an experimental physicist say about their research?")
        #                            ,("q10c", "How important for earning a good grade in this class was understanding the theoretical equations provided in the lab guide?")
        #                            ,("q11a", "Computers are helpful for plotting and analyzing data. What do YOU think?")
        #                            ,("q11b", "Computers are helpful for plotting and analyzing data. What would an experimental physicist say about their research?")
        #                            ,("q11c", "How important for earning a good grade in this class was using a computer for plotting and analyzing data?")
        #                            ,("q12a", "When I am doing an experiment, I try to make predictions to see if my results are reasonable. What do YOU think?")
        #                            ,("q12b", "When I am doing an experiment, I try to make predictions to see if my results are reasonable. What would an experimental physicist say about their research?")
        #                            ,("q12c", "How important for earning a good grade in this class was making predictions to see if my results are reasonable?")
        #                            ,("q13a", "When doing an experiment I usually think up my own questions to investigate. What do YOU think?")
        #                            ,("q13b", "When doing an experiment I usually think up my own questions to investigate. What would an experimental physicist say about their research?")
        #                            ,("q13c", "How important for earning a good grade in this class was thinking up my own questions to investigate?")
        #                            ,("q14a", "When doing an experiment, I just follow the instructions without thinking about their purpose. What do YOU think?")
        #                            ,("q14b", "When doing an experiment, I just follow the instructions without thinking about their purpose. What would an experimental physicist say about their research?")
        #                            ,("q14c", "How important for earning a good grade in this class was thinking about the purpose of the instructions in the lab guide?")
        #                            ,("q15a", "Designing and building things is an important part of doing physics experiments. What do YOU think?")
        #                            ,("q15b", "Designing and building things is an important part of doing physics experiments. What would an experimental physicist say about their research?")
        #                            ,("q15c", "How important for earning a good grade in this class was designing and building things?")
        #                            ,("q16a", "When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor. What do YOU think?")
        #                            ,("q16b", "When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor. What would an experimental physicist say about their research?")
        #                            ,("q16c", "How important for earning a good grade in this class was overcoming difficulties without the instructor's help?")
        #                            ,("q17a", "A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away. What do YOU think?")
        #                            ,("q17b", "A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away. What would an experimental physicist say about their research?")
        #                            ,("q17c", "How important for earning a good grade in this class was randomly changing things to fix a problem with the experiment?")
        #                            ,("q18a", "Communicating scientific results to peers is a valuable part of doing physics experiments. What do YOU think?")
        #                            ,("q18b", "Communicating scientific results to peers is a valuable part of doing physics experiments. What would an experimental physicist say about their research?")
        #                            ,("q18c", "How important for earning a good grade in this class was communicating scientific results to peers?")
        #                            ,("q19a", "I am able to read a scientific journal article for understanding. What do YOU think?")
        #                            ,("q19b", "I am able to read a scientific journal article for understanding.  What would an experimental physicist say about their research?")
        #                            ,("q19c", "How important for earning a good grade in this class was reading scientific journal articles?")
        #                            ,("q20a", "Working in a group is an important part of doing physics experiments. What do YOU think?")
        #                            ,("q20b", "Working in a group is an important part of doing physics experiments. What would an experimental physicist say about their research?")
        #                            ,("q20c", "How important for earning a good grade in this class was working in a group?")
        #                            ,("q21a", "If I am writing a lab report, my main goal is to make conclusions based on my data using scientific reasoning. What do YOU think?")
        #                            ,("q21b", "If I am writing a lab report, my main goal is to make conclusions based on my data using scientific reasoning. What would an experimental physicist say about their research?")
        #                            ,("q21c", "How important for earning a good grade in this class was writing a lab report that made conclusions based on data using scientific reasoning?")
        #                            ,("q22a", "If I am writing a lab report, my main goal is to create a report with the correct sections and formatting.  What do YOU think?")
        #                            ,("q22b", "If I am writing a lab report, my main goal is to create a report with the correct sections and formatting. What would an experimental physicist say about their research?")
        #                            ,("q22c", "How important for earning a good grade in this class was writing a lab report with the correct sections and formatting?")
        #                            ,("q23a", "I enjoy building things and working with my hands. What do YOU think?")
        #                            ,("q23b", "I enjoy building things and working with my hands. What would an experimental physicist say about their research?")
        #                            ,("q24a", "I don't enjoy doing physics experiments. What do YOU think?")
        #                            ,("q24b", "I don't enjoy doing physics experiments.  What would an experimental physicist say about their research?")
        #                            ,("q25a", "Nearly all students are capable of doing a physics experiment if they work at it. What do YOU think?")
        #                            ,("q25b", "Nearly all students are capable of doing a physics experiment if they work at it.  What would an experimental physicist say about their research?")
        #                            ,("q26a", "If I try hard enough I can succeed at doing physics experiments.  What do YOU think?")
        #                            ,("q26b", "If I try hard enough I can succeed at doing physics experiments.  What would an experimental physicist say about their research?")
        #                            ,("q27a", "If I wanted to, I think I could be good at doing research. What do YOU think?")
        #                            ,("q27b", "If I wanted to, I think I could be good at doing research. What would an experimental physicist say about their research?")
        #                            ,("q28a", "When I approach a new piece of lab equipment, I feel confident I can learn how to use it well-enough for my purposes. What do YOU think?")
        #                            ,("q28b", "When I approach a new piece of lab equipment, I feel confident I can learn how to use it well-enough for my purposes. What would an experimental physicist say about their research?")
        #                            ,("q28c", "How important for earning a good grade in this class was learning to use a new piece of laboratory equipment?")
        #                            ,("q29a", "I do not expect doing an experiment to help my understanding of physics. What do YOU think?")
        #                            ,("q29b", "I do not expect doing an experiment to help my understanding of physics. What would an experimental physicist say about their research?")
        #                            ,("q30a", "The primary purpose of doing a physics experiment is to confirm previously known results. What do YOU think?")
        #                            ,("q30b", "The primary purpose of doing a physics experiment is to confirm previously known results. What would an experimental physicist say about their research?")
        #                            ,("q30c", "How important for earning a good grade in this class was confiming previously known results?")
        #                            ,("q31a", "Physics experiments contribute to the growth of scientific knowledge. What do YOU think?")
        #                            ,("q31b", "Physics experiments contribute to the growth of scientific knowledge. What would an experimental physicist say about their research?")
        #                            ,("q40a", "We use this statement to discard the survey of people who are not reading the questions. Please sele...-What do YOU think when doing experiments for class?")
        #                            ,("q40b", "We use this statement to discard the survey of people who are not reading the questions. Please sele...-What would experimental physicists say about their research?")]

        #self.questionIDToQuestionText = dict(self.questionIDToQuestionText)
        
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
                       ,'q30a','q30b','q31a','q31b']#,'q40a','q40b']

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

    def questionList(self):

       return [['Question Number', 'Personal/Professional Statement', 'How important for earning a good grade in this class was...'], ['1', 'When doing an experiment, I try to understand how the experimental setup works.', '... understanding how the experimental setup works?'], ['2', "I don't need to understand how the measurement tools and sensors work in order to carry out an experiment.", '... understanding how the measurement tools and sensors work?'], ['3', "When doing a physics experiment, I don't think much about sources of systematic error.", '... thinking about sources of systematic error?'], ['4', 'It is helpful to understand the assumptions that go into making predictions.', '... understanding the approximations and simplifications that are included in theoretical predictions?'], ['5', 'Whenever I use a new measurement tool, I try to understand its performance limitations.', '... understanding the performance limitations of the measurement tools?'], ['6', 'Calculating uncertainties usually helps me understand my results better.', '... calculating uncertainties to better understand my results?'], ['7', "If I don't have clear directions for analyzing data, I am not sure how to choose an appropriate analysis method.", '... choosing an appropriate method for analyzing data (without explicit direction)?'], ['9', 'I am usually able to complete an experiment without understanding the equations and physics ideas that describe the ...', '... understanding the equations and physics ideas that describe the system I am investigating?'], ['10', 'When doing an experiment, I try to understand the relevant equations.', '... understanding the relevant equations?'], ['11', 'Computers are helpful for plotting and analyzing data.', '... using a computer for plotting and analyzing data?'], ['12', 'When I am doing an experiment, I try to make predictions to see if my results are reasonable.', '... making predictions to see if my results are reasonable?'], ['13', 'When doing an experiment I usually think up my own questions to investigate.', '... thinking up my own questions to investigate?'], ['14', 'When doing an experiment, I just follow the instructions without thinking about their purpose.', '... thinking about the purpose of the instructions in the lab guide?'], ['15', 'Designing and building things is an important part of doing physics experiments.', '... designing and building things?'], ['16', 'When I encounter difficulties in the lab, my first step is to ask an expert, like the instructor.', "... overcoming difficulties without the instructor's help?"], ['17', 'A common approach for fixing a problem with an experiment is to randomly change things until the problem goes away.', '... randomly changing things to fix a problem with the experiment?'], ['18', 'Communicating scientific results to peers is a valuable part of doing physics experiments.', '... communicating scientific results to peers?'], ['19', 'Scientific journal articles are helpful for answering my own questions and designing experiments', '... reading scientific journal articles?'], ['20', 'Working in a group is an important part of doing physics experiments.', '... working in a group?'], ['21', 'If I am communicating results from an experiment, my main goal is to make conclusions based on my data using scienti...', '... making conclusions based on data using scientific reasoning?'], ['22', 'If I am communicating results from an experiment, my main goal is to create a report with the correct sections and f...', '... communicating results with the correct sections and formatting?'], ['23', 'I enjoy building things and working with my hands.', 'NA'], ['24', "I don't enjoy doing physics experiments.", 'NA'], ['25', 'Nearly all students are capable of doing a physics experiment if they work at it.', 'NA'], ['26', 'If I try hard enough I can succeed at doing physics experiments.', 'NA'], ['27', 'If I wanted to, I think I could be good at doing research.', 'NA'], ['28', 'When I approach a new piece of lab equipment, I feel confident I can learn how to use it well enough for my purposes.', '... learning to use a new piece of laboratory equipment?'], ['29', 'I do not expect doing an experiment to help my understanding of physics.', 'NA'], ['30', 'The primary purpose of doing a physics experiment is to confirm previously known results.', '... confiming previously known results?'], ['31', 'Physics experiments contribute to the growth of scientific knowledge.', 'NA']]



