#!/bin/bash

if [ $# == '1' ]
then
	if [[ "$1" = "debug" ]]
	then
		~/dev/google_appengine/dev_appserver.py src/web/meneapp/
	else
		~/dev/google_appengine/appcfg.py --oauth2 --email='albertfdp@gmail.com' update src/web/meneapp
	fi
fi