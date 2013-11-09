import webapp2
import jinja2
import os
import hashlib

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../view')))

class AboutHandler(webapp2.RequestHandler):
    
    def get(self):
        
    	template_values = {
            'title': 'Meneame',
			'project_name': 'Meneapp',
			'albert_hash': hashlib.md5('albertfdp@gmail.com').hexdigest(),
			'ferdinando_hash': hashlib.md5('ferdinando.papale@gmail.com').hexdigest(),
			'jose_hash': hashlib.md5('th0rg4l@gmail.com').hexdigest()
        }
    
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.write(template.render(template_values))