import telebot
import requests
import config
import postgres
from telebot import types

url = config.weatherURL # url for JSON request to get weather data
bot = telebot.TeleBot(config.token) #Bot
w_api = config.WeatherApi # Open Weather API

#connecting to Database
db = postgres.Db()
db.connect()

# getting list of languages to change lang.
def gen_change_markup():
    markup = types.InlineKeyboardMarkup()
    lst = db.getAllLang()
    for i in lst:
        markup.add(types.InlineKeyboardButton(text=i[0], callback_data=(str(i[1]) + '/1/' + str(i[0]))))
    return markup

#gettin cities shorcuts for user
def ret(uid):
    mp = types.ReplyKeyboardMarkup()
    cities = db.getCityNamesForUser(uid)
    for i in cities:
        mp.add(i[0])
    return mp


#command: start
@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id #chat id
    user_id = message.from_user.id #user id of private chat
    username = message.from_user.first_name #first name of user
    surname = message.from_user.last_name #last name of user

    # markup for city shortcut
    mp = ret(user_id)

    #preparing sticker
    sti = open('Stickers/hello.webp', 'rb')

    #sendin message
    bot.send_sticker(chat_id, sti)
    bot.send_message(chat_id, 'Hello dude!\nWanna see weather?\nJust type city name.', reply_markup = mp)

    #adding user to database if it is his/her first time using bot
    if not db.user_exists(user_id):
        db.add_user(user_id, username, surname)


#command: my language
@bot.message_handler(commands=['my_lang'])
def change_lang(message):
    lng = db.getLang(message.from_user.id)
    bot.send_message(message.chat.id, 'You current language is ' +  lng[0])


#command: help
@bot.message_handler(commands=['help'])
def mes(message):
    sti = open('Stickers/help.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Hello I am weather bot, created by @ozhek,\n'
                                      'You can use /change_lang - to change language,\n'
                                      '/my_lang to see what language do you use\n'
                                      '/remove_short to remove city from shortcuts list\n'
                                      'and just type city name to get weather in that city', parse_mode='html')


#command: remove shortcut
@bot.message_handler(commands=['remove_short'])
def remove_sh(message):
    #preparing data
    chat_id = message.chat.id
    uid = message.from_user.id

    #request for gettin list of cities for user
    lst = db.getCitiesForUser(uid)

    #markup for convinience
    mp = types.InlineKeyboardMarkup()
    for i in lst:
        mp.add(types.InlineKeyboardButton(text=i[0], callback_data=str(i[1])+'/3/'))

    #sendin message
    bot.send_message(chat_id, 'Choose city to remove from shortcuts:', reply_markup=mp)


@bot.callback_query_handler(func=lambda call: '/3/' in call.data)
def callback_rem(call):
    try:
        if call.message:
            #preparing data
            ll = list(call.data.split('/3/'))
            cid = int(ll[0])
            uid = call.from_user.id

            #deleting from database
            db.delete_cu(cid, uid)
    except Exception as e:
        print(4)
        print(e)
    finally:
        #deleting message
        bot.delete_message(call.message.chat.id, call.message.message_id)

        # updating shortcut list
        mp = ret(call.from_user.id)
        bot.send_message(call.message.chat.id, 'Congrats, we removed city from shortcuts.', reply_markup=mp)


#command: change language
@bot.message_handler(commands=['change_lang'])
def change_lang(message):
    markup = gen_change_markup()
    bot.send_message(message.chat.id, 'Choose language', reply_markup=markup)


#callback handler for changing language
@bot.callback_query_handler(func=lambda call: '/1/' in call.data)
def callback(call):
    try:
        if call.message:
            #gettin language and user data
            ll = list((call.data).split('/1/'))
            lang = ll[0]
            l_name = ll[1]
            user_id = call.from_user.id

            #database request for changing language for user
            db.changeLang(lang, user_id)

            # sendin message
            bot.send_message(call.message.chat.id, 'Language have been changed to ' + l_name)
    except Exception as e:
        print(1)
        print(e)
    finally:
        #gettin rid of message
        bot.delete_message(call.message.chat.id, call.message.message_id)


#function for showing weather and adding city to shortcut
@bot.message_handler(content_types=['text'])
def weather_send(message):
    try:
        #preparing data
        city_name = message.text
        user_id = message.from_user.id
        lang = db.getLang(user_id)

        #JSON request to openweathermap.org for gettin weather
        params = {'q': city_name, 'appid': w_api, 'units': 'metric', 'lang': lang[1]}
        result = requests.get(url, params=params)
        weather = result.json()

        #preparing data
        cid = int(weather['id'])
        c_name = weather['name']
        cn_id = weather['sys']['country']

        #image for weather
        im = open('icons/' + weather['weather'][0]['icon'] + '.png', 'rb')

        #markup for adding to shortcut
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton(text='Save city', callback_data=str(cid) + '/2/' + str(user_id))
        markup.add(item)

        #message text
        txt = "<b>" + weather["name"] + ", " + weather['sys']['country']+"</b> \n" + "| <i>Description</i>: " + str(weather['weather'][0]["description"]) + "\n" + "| <i>Temperature: </i>\n" + "| <i>Feels like</i>: " + str(weather["main"]["feels_like"]) + " °C \n" + "| <i>Actually</i>: " + str(weather["main"]['temp']) + " °C \n" + "| <i>Wind speed</i>: " + str(float(weather['wind']['speed'])) + " м/с \n" + "| <i>Humidity</i>: " + str(int(weather['main']['humidity'])) + "%\n"

        #adding city to database if we don't have it
        if not db.findCity(cid):
            db.insertCity(cid,c_name, cn_id)

        #removing markup if we already have it
        if db.finduc(cid, user_id):
            markup = None

        #sending message
        bot.send_photo(message.chat.id, im)
        bot.send_message(message.chat.id, text=txt, parse_mode='html', reply_markup=markup)
    except Exception as e:
        print(2)
        print(e)

        #the case when we don't find the city
        sti = open('Stickers/please.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        bot.send_message(message.chat.id, 'Hey, I can\'t find this city, pleas check correctness.')


#callback handler for adding city to shortcut
@bot.callback_query_handler(func=lambda call: '/2/' in call.data)
def callb(call):
    try:
        if call.message:
            #preparing data
            ll = call.data.split('/2/')
            cid = ll[0]
            uid = ll[1]

            #adding city into database for particular user
            db.insert_cu(int(cid), int(uid))
    except Exception as e:
        print(3)
        print(e)
    finally:
        #removing markup from weather message
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text=call.message.text, reply_markup=None)

        #updating shortcut list
        mp = ret(call.from_user.id)
        bot.send_message(call.message.chat.id, 'Congrats, we added city to shortcuts.', reply_markup=mp)


# RUN
bot.polling(none_stop=True)
