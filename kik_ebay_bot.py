"""

It's designed to greet the user, send a suggested response and replies to them with their profile picture.
Remember to replace the BOT_USERNAME_HERE, BOT_API_KEY_HERE and WEBHOOK_HERE fields with your own.

See https://github.com/kikinteractive/kik-python for Kik's Python API documentation.

Apache 2.0 License

(c) 2016 Kik Interactive Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

"""

from flask import Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, PictureMessage, \
    SuggestedResponseKeyboard, TextResponse, StartChattingMessage
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from ebaysdk.finding import Connection as finding
import ConfigParser



class KikBot(Flask):
    """ Flask kik bot application class"""

    def __init__(self, kik_api, import_name, static_path=None, static_url_path=None, static_folder="static",
                 template_folder="templates", instance_path=None, instance_relative_config=False,
                 root_path=None):

        self.kik_api = kik_api

        super(KikBot, self).__init__(import_name, static_path, static_url_path, static_folder, template_folder,
                                     instance_path, instance_relative_config)

        self.route("/incoming", methods=["POST"])(self.incoming)

    def incoming(self):
        """Handle incoming messages to the bot. All requests are authenticated using the signature in
        the 'X-Kik-Signature' header, which is built using the bot's api key (set in main() below).
        :return: Response
        """
        # verify that this is a valid request
        if not self.kik_api.verify_signature(
                request.headers.get("X-Kik-Signature"), request.get_data()):
            return Response(status=403)

        messages = messages_from_json(request.json["messages"])

        keywords = self.get_config()

        response_messages = []

        for message in messages:
            user = self.kik_api.get_user(message.from_user)    

            # Check if the user has sent a text message.
            if isinstance(message, TextMessage):
                user = self.kik_api.get_user(message.from_user)
                message_body = message.body.lower()


                if any(keyword in message_body for keyword in keywords):

                    response_data = self.get_ebay_data(config, message_body, "laptop")
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=response_data))

                else:                        
                    response_messages.append(TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=self.get_regular_trained_data(message_body),
                        keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("Good"), TextResponse("Bad")])]))


            # If its not a text message, give them another chance to use the suggested responses
            else:

                response_messages.append(TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body="Sorry, I didn't quite understand that. How are you, {}?".format(user.first_name),
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("Good"), TextResponse("Bad")])]))


            self.kik_api.send_messages(response_messages)

    
        return Response(status=200)

    @staticmethod
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


        dictstr = response.dict()
        return dictstr['itemSearchURL']

    # This returns regularly trained based on the query using Chatterbot
    @staticmethod
    def get_regular_trained_data(userText):
        english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
        english_bot.set_trainer(ChatterBotCorpusTrainer)
        english_bot.train("chatterbot.corpus.english.greetings")
    
        return str(english_bot.get_response(userText))


    @staticmethod
    def get_config():
        config = ConfigParser.ConfigParser()
        config.read("config.cfg")
        keywords = config.get("shopping", "list").split(",")
       
       return keywords


if __name__ == "__main__":
    """ Main program """
    kik = KikApi('', '')
    # For simplicity, we're going to set_configuration on startup. However, this really only needs to happen once
    # or if the configuration changes. In a production setting, you would only issue this call if you need to change
    # the configuration, and not every time the bot starts.
    kik.set_configuration(Configuration(webhook='http://54307f9f.ngrok.io/incoming'))
    app = KikBot(kik, __name__)
    app.run(port=8080, host='127.0.0.1', debug=True)
