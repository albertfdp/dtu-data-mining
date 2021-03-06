#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import fix_path
from control import main, time, about, sentiment, network, topics

app = webapp2.WSGIApplication([
    ('/', main.MainHandler),
    ('/index', main.MainHandler),
	('/time', time.TimeHandler),
	('/sentiment', sentiment.SentimentHandler),
	('/network', network.NetworkHandler),
	('/topics', topics.TopicsHandler),
	('/about', main.MainHandler)
], debug=True)
