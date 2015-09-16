# pylint: disable=C0321
# pylint: disable=C0303
# pylint: disable=line-too-long
import jinja2
import os
import csv
from Questions import Questions

class Report(Questions):
    """
    This class generates an html report based on
    graphs produced by the plotting class

    It should be initialized with:
   
    (1) the  table values for table 1
    (2) the page value which can be:
        # "report" - the main report page
        # "howtoread" - the how to read this report page
        # "analysis" - the how this report was analyzed page
        # "questionlist" - the question list page
    (3) templateVars which requires:
        # title (typically university name)
        # email (for contacting ECLASS representatives)
    """

    def __init__(self, tableVals, templateVars, page, dir, debug=False):
        
        self.debug = debug

        self.dir = dir

        # Check if tableVals is the correct length (doesn't validate the order)
        if len(tableVals) == 5:
            self.tableVals = tableVals
        else:
            raise ValueError("""Needs to the following 5 values:

                                Number of valid pre-responses"
                                Number of valid post-responses"
                                Number of matched responses"
                                Reported number of students in class"
                                Fraction of class participating in pre and post""")
        



        # Check if templateVars has the right values
        self._keys = ["title", "email"]
        for k in self._keys:
            if k in templateVars:
                print(k + " present")
            else:
                raise ValueError(k + " NOT PRESENT!")
                

        # every directory should have it's own "howto", "analysis", and 
        # "questionlist" pages. This way users can link back and forth
        # between the pages.
        self.page = ["report", "howtoread", "analysis", "questionlist"]


        self.templateVars = templateVars
        
        # jinja2 class variables
        self.templateLoader = jinja2.FileSystemLoader(searchpath=os.getcwd())
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.template = self.templateEnv.get_template("template.html")


    def _MakeNavbar(self):
        """
        Adds the navbar titles

        edit here if you want to include more tabs in the navbar
        note: you will need to edit the template as well to create
        these tabs
        """
        self.templateVars["navbar"] = zip(["Report", "How to Read This Report", "How This Report was Analyzed", "Question List"]
                                          ,["report.html", "howtoread.html", "analysis.html", "questionlist.html"])

    #def _MakeQuestionList(self):
    #    """
    #    returns question list from csv formated like:
    #    (question number, question type 1, question type 2)
    #    """

    #    with open(os.getcwd()+'/data/questionlist.csv', 'rt') as ql:
    #        reader = csv.reader(ql)
    #        questionlist = [row for row in reader]
        
    #        self.templateVars["questionlist"] = questionlist

    def _MakeQuestionList(self):
        self.templateVars["questionlist"] = self.questionList() 


    def _MakeTable(self):
        """
        creates the table values to insert into the templateVars dictionary
        """

        table = zip(["Number of valid pre-responses"
                    ,"Number of valid post-responses"
                    ,"Number of matched responses"
                    ,"Reported number of students in class"
                    ,"Fraction of class participating in pre and post"
                    ],self.tableVals)
        self.templateVars['table1'] = table

    def _ProcessTemplate(self):
        outputText = self.template.render(self.templateVars)
        return outputText

    def GenerateReport(self):
        """
        Generates report
        """

        # every directory should have it's own "howto", "analysis", and 
        # "questionlist" pages. This way users can link back and forth
        # between the pages.
        
        for p in self.page:

            self.templateVars["page"] = p
            
            with open(self.dir + "\\" + p + ".html", "wb+") as index:
                self._MakeNavbar()
                self._MakeQuestionList()
                self._MakeTable()
                outputText = self._ProcessTemplate()
                index.write(outputText.encode())
                index.close()

if __name__ == "__main__":
    R = Report(tableVals=[1,2,3,4,0.5]
               , templateVars={"title":"Example", "email":"mailto:replace@me.com"}
               , page="report"
               , debug=True
               , dir='C:\\Users\\John\\Source\\Repos\\ECLASS-Report-Generator')
    R.GenerateReport()
