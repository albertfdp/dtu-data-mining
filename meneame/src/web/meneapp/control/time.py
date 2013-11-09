import webapp2
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../view')))

class TimeHandler(webapp2.RequestHandler):

	def get(self):
		
		template_values = {
			'title': 'meneapp'
		}
		
	