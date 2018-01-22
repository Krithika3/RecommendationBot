from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import ebaysdk
import ConfigParser
from ebaysdk.finding import Connection as finding

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

# This method is used to get bot responses.
@app.route("/get")
def get_bot_response():

    config = ConfigParser.ConfigParser()
    
    config.read("config.cfg")

    keywords = config.get("shopping", "list").split(",")

    userText = request.args.get('msg')

    #Check all words in the config dictionary to see the kind of word.
    for keyword in keywords:
        if keyword in userText:
            return get_ebay_data(config, userText, keyword)         
            
        else:

            return get_regular_trained_data(userText)
    
# This method is used to get data based on keywords to see if we can get ebay links based on the API       

def get_ebay_data(config, userText, keyword):
    
    site_id = config.get('ebay', 'site_id')
    app_id = config.get('ebay', 'app_id')
    max_price = config.get('ebay', 'max_price')
    min_price = config.get('ebay', 'min_price')
    sort_order = config.get('ebay', 'sort_order')

    api = finding(siteid=site_id,appid=app_id, config_file=None)
    response = api.execute('findItemsAdvanced', {
            'keywords': keyword,
            'itemFilter': [
                {'name': 'Condition', 'value': 'Used'},
                {'name': 'MinPrice', 'value': min_price, 'paramName': 'Currency', 'paramValue': 'USD'},
                {'name': 'MaxPrice', 'value': max_price, 'paramName': 'Currency', 'paramValue': 'USD'}
            ],
            'sortOrder': sort_order
        })


    item_response = response.dict()
    return item_response['itemSearchURL']
 

# This returns regularly trained based on the query using Chatterbot
def get_regular_trained_data(userText):
    english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
    english_bot.set_trainer(ChatterBotCorpusTrainer)
    english_bot.train("chatterbot.corpus.english.greetings")
    
    return str(english_bot.get_response(userText))



if __name__ == "__main__":
    app.run()
