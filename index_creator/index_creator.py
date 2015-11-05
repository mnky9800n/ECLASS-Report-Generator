
import jinja2
import os
import sys

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

#program_call, report_directory = sys.argv
report_directory = r'C:\Users\John\Source\Repos\ECLASS-Report-Generator\data'

directories = get_immediate_subdirectories(report_directory)

print([d for d in directories])

TemplateLoader = jinja2.FileSystemLoader(searchpath='C:\\Users\\John\\Source\\Repos\\ECLASS-Report-Generator\\index_creator\\')


TemplateEnv = jinja2.Environment(loader=TemplateLoader)
Template = TemplateEnv.get_template('directory_template.html')
RenderedTemplate = Template.render({'directories':directories})

with open(file='index.html', mode='wb') as f:
    f.write(RenderedTemplate.encode())
    f.close() 