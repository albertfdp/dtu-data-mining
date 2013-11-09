Data mining menéame
=========================

## Google App Engine

#### How to run it

In order to run the web you need to download the Google App Engine kit from [here](https://developers.google.com/appengine/).

Then you can find the script **upload_to_appengine.sh** in the root of this project. You'll probably need to modify the path to match your installation directory. Afterwards you can debug doing:

`
	./upload_to_appengine.sh debug
`

And deploy using:

`
	./upload_to_appengine.sh
`

You might need to give execution permissions `chmod +x upload_to_appengine.sh`.