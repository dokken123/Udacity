import jinja2
import os
import re

def validInput(value,regex_str):
	regexp = re.compile(regex_str)
	return (regexp.match(value) != None) and 1 or 0

_jinja2_environment = jinja2.Environment(autoescape=False,
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

def renderTemplate(template_path,template_value):
	template = _jinja2_environment.get_template(template_path)
	return template.render(template_value)

