import telebot
from telebot import types
import requests
import json

bot = telebot.TeleBot('6960208989:AAHlBJpA0-5xwJIWJv5tamJjofDlyRwfgWs')
weather_API = 'd26cd5944a376e41b3b56cab18208c18'
edamam_key = '4e1ae2986b7c7d4c71f2db5ef1e37ba0'
edamam_id = '58ee370c'

weather_descriptions = {
    "clear sky": "Ясное небо",
    "few clouds": "Малооблачно",
    "scattered clouds": "Рассеянные облака",
    "broken clouds": "Облачно с прояснениями",
    "shower rain": "Ливень",
    "rain": "Дождь",
    "thunderstorm": "Гроза",
    "snow": "Снег",
    "mist": "Туман",
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # # Поле для кнопок
    # markup = types.ReplyKeyboardMarkup()
    #
    # # Кнопки
    # btn1 = types.KeyboardButton('Посмотреть рецепты')
    # btn2 = types.KeyboardButton('Что можно сделать из моих продуктов')
    # btn3 = types.KeyboardButton('Посмотреть погоду')
    # markup.row(btn1, btn3)
    # markup.row(btn2)

    # Вступительное сообщение
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}\nГотовы сделать что-нибудь вкусненькое? 😋\nПосмотрим погоду или рецепты?')
                     # , reply_markup=markup)


@bot.message_handler(commands=["weather"])
def get_weather(message):
    bot.send_message(message.chat.id, "В каком городе ты сейчас находишься:")
    bot.register_next_step_handler(message, weather_city)


def weather_city(message):
    city = message.text.strip().lower()
    res_weather = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_API}&units=metric')
    if res_weather.status_code == 200:
        data = json.loads(res_weather.text)
        temp_grad = data["main"]["temp"]
        temp_osh = data["main"]["feels_like"]
        weather_description_en = data["weather"][0]["description"]
        # Перевод описания погоды
        weather_description_ru = weather_descriptions.get(weather_description_en, weather_description_en)
        caption = (f'Погода сейчас: {temp_grad}°C. Ощущается как {temp_osh}°C. {weather_description_ru}')

        image = 'cloudy.png' if temp_grad > 25.0 else 'rainy.png'
        file = open('./' + image, 'rb')
        bot.send_photo(message.chat.id, file, caption=caption)
    else:
        bot.reply_to(message.chat.id, "Города не существует или указан неверно")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """<em>/start - старт работы бота</em>
<em>Рецепты - рецепт, который нужно найти</em>""", parse_mode='html')


@bot.message_handler(commands=['recipe'])
def get_recipe(message):
    bot.send_message(message.chat.id, 'Давай посмотрим, какой рецепт тебе нужен: ')
    bot.register_next_step_handler(message, show_recepies)

def show_recepies(message):
    message_list = message.text.strip().lower()
    url_edamam = f'https://api.edamam.com/search?q={message_list}&app_id={edamam_id}&app_key={edamam_key}'
    res_url_edamam = requests.get(url_edamam)
    if res_url_edamam.status_code == 200:
         data_recipe = json.loads(res_url_edamam.text)
         for hit in data_recipe["hits"][:5]:
             recipe_label = hit["recipe"]["label"]
             recipe_url = hit["recipe"]["url"]
             recipe_calories = hit["recipe"]["calories"]
             ingredients = '\n'.join(hit["recipe"]['ingredientLines'])
             bot.send_message(message.chat.id, f"<b>Название блюда/напитка - {recipe_label}</b>.\nКол-во калорий - {recipe_calories}\n"
                                               f"<em>Ингридиенты блюда/напитка:\n{ingredients}.</em>\nСсылка на рецепт - {recipe_url}\n", parse_mode="html")
    else:
        bot.send_message(message.chat.id, "Рецепт не найден или продукты введены некорректно")




@bot.message_handler()
def core(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет еще раз, друг!\nГотов сделать что-нибудь вкусненькое? 😋\nПосмотрим погоду, рецепты? Напиши, что тебе нужно:')


bot.polling(none_stop=True)
