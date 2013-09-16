class Article(object):
	
	_title = ""
	_url = ""
	_user = ""
	_clicks = 0
	_votes = 0
	_story_url = ""
	_description = ""
	_comment_counter = 0
	_comments = []
	
	def to_csv(self):
		return ';'.join([self._url, self._user, str(self._votes), self._story_url, str(self._clicks), 
						self._description.replace(";", ""), str(self._comment_counter)])
	
	def to_string(self):
		return '%s;%s;%d;%d;%d;' % (self._user, self._title, self._votes, self._clicks, self._comment_counter)
	
	@property
	def title(self):
		return self._title
	
	@title.setter
	def title(self, title):
		self._title = title
		
	@property
	def comments(self):
		return self._comments
	
	@comments.setter
	def comments(self, comments):
		self._comments = comments
		
	@property
	def url(self):
		return self._url
	
	@url.setter
	def url(self, url):
		self._url = url
		
	@property
	def user(self):
		return self._user
	
	@user.setter
	def user(self, user):
		self._user = user
		
	@property
	def clicks(self):
		return self._clicks
	
	@clicks.setter
	def clicks(self, clicks):
		self._clicks = clicks
		
	@property
	def votes(self):
		return self._votes
	
	@votes.setter
	def votes(self, votes):
		self._votes = votes
		
	@property
	def story_url(self):
		return self._story_url
	
	@story_url.setter
	def story_url(self, story_url):
		self._story_url = story_url
		
	@property
	def description(self):
		return self._description
	
	@description.setter
	def description(self, description):
		self._description = description
		
	@property
	def comment_counter(self):
		return self._comment_counter
	
	@comment_counter.setter
	def comment_counter(self, comment_counter):
		self._comment_counter = comment_counter