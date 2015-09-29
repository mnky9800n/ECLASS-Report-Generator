# ECLASS-Report-Generator

A command line utility that:

1. cleans E-CLASS data from Qualtrics
2. generates static web page reports on student E-CLASS performance


Tested in Python 3.4.

# How To Use

Runs from the command line with the following *required* args:

1. path to pre-historical data
2. path to post-historical data
3. path to course data CSVs
4. path to instructor survey data

This will produce 

1. a folder for each class titled by the course ID as reported by Qualtrics with the month and year appended
2. each folder will have an image directory
3. each image directory will have the following images: currentinterest.png, declaredmajor.png, expertvsyou1.png, expertvsyou2.png, futureplans.png, gender.png, grades1.png, grades2.png, gradespart1.png, overall.png, whatdoyouthink1.png, whatdoyouthink2.png
4. <not implemented> report.html
5. <not implemented> howtoread.html
6. <not implemented> questionlist.html
7. <not implemented> analysis.html
