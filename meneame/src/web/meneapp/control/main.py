import webapp2
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../view')))

class MainHandler(webapp2.RequestHandler):
    
    def get(self):
        
        template_values = {
            'title': 'Meneame',
			'project_name': 'Meneapp'
        }
    
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))