# A simple shopping bot with ChatterBot and ebaySdk

## Local Setup:
 1. Ensure that Python, Flask, SQLAlchemy, ChatterBot, ebaysdj are installed (either manually, or run `pip install -r requirements.txt`).
 2. Run *app.py*
 3. App will be available[http://localhost:5000/](http://localhost:5000/)

## What does this app do?
This app uses ChatBot and the ebaysdk to respond to common messages. It responds to common english greetings using  ChatterBot(https://github.com/chamkank/flask-chatterbot) and responds to some purchase related requests using the ebaysdk(https://github.com/timotheus/ebaysdk-python)

The config.cfg file contains a list of keywords which trigger off to get data from the ebay sdk or Chatterbot

## Integration with Kik