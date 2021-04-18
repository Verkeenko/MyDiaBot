import random
import pandas as pd
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
import telebot
import re
from random import randint
import config
import dbworker

bot = telebot.TeleBot(config.token)

import telebot

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я помогу рассчитать необходимую дозу инсулина '
                                      'Внимание расчеты являются приблизительными необходимо придерживаться '
                                      'рекомендаций своего лечаещего врача. Если Вы знаете свою чувствительность '
                                      ' к инсулину нажмите /YES , если нет то нажмите /no  либо  /help')


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Бот создан для примерного расчета инсулина для старта и возврата '
                                      'в начало нажмите /start, в процессе используйте команды /YES,/no, /next Желаем хороших сахаров')


@bot.message_handler(commands=['no'])
def cdi_message(message):
    bot.send_message(message.chat.id, 'Привет, я помогу рассчитать фактор чувствительности инсулина, '
                                      'если согласен нажми /calculate если нет то, /start либо /help')


@bot.message_handler(commands=['calculate'])
def start(message):
    bot.send_message(message.from_user.id, "введите суточную дозу инсулина: ");
    bot.register_next_step_handler(message, get_name);  # следующий шаг – функция get_name


def get_name(message):  # рассчитываем по формуле фактор чувствительности инсулина
    global fci;
    global cdi
    cdi = message.text;
    fci = 100 / float(cdi)
    bot.send_message(message.from_user.id,
                     f'одна единица инсулина снизит снизит сахар на {fci} ммоль /next либо /help');
    bot.register_next_step_handler(message, get_sugar)


@bot.message_handler(commands=['YES'])
def get_cd(message):
    bot.send_message(message.from_user.id, "на сколько грамм углеводов Вы колите 1 ед. инсулина либо /help");
    bot.register_next_step_handler(message, get_xe_cdi);


def get_xe_cdi(message):  # рассчитываем по формуле фактор чувствительности инсулина
    global xe_cdi;
    xe_cdi = float(message.text);
    bot.send_message(message.from_user.id,
                     f'одна единица инсулина позволит усвоить {xe_cdi} гр. углеводов /GO либо /help');
    bot.register_next_step_handler(message, get_cdi)


@bot.message_handler(commands=['GO'])
def get_cdi(message):
    bot.send_message(message.from_user.id, 'введите цифрами на сколько ммоль\на литр снижает '
                                           'сахар одна единица инсулина либо /help');
    bot.register_next_step_handler(message, get_fci);


def get_fci(message):  # рассчитываем по формуле фактор чувствительности инсулина
    global fci;
    fci = float(message.text);
    bot.send_message(message.from_user.id,
                     f'одна единица инсулина снизит снизит сахар на {fci} ммоль /next либо /help');
    bot.register_next_step_handler(message, get_sugar)


@bot.message_handler(commands=['next'])
def get_sugar(message):
    bot.send_message(message.from_user.id, 'теперь давай рассчитаем сколько нужно ввсести инсулина, '
                                           'для этого введи значение сахара ');
    bot.register_next_step_handler(message, get_ins);


def get_ins(message):
    global sugar;
    sugar = float(message.text);
    bot.send_message(message.from_user.id, 'теперь введите пожалуйста сколько углеводов планируете сьесть: ');
    bot.register_next_step_handler(message, get_xe)


def get_xe(message):
    global xe;
    insulin = []
    xe = float(message.text);
    if xe_cdi >= 0:
        insulin = xe_cdi
    else:
        i = 500 / float(cdi)  # формула расчета инсулина на хлебные единицы
        insulin = i
    if sugar >= 5 and sugar <= 8:
        res = float(xe) / float(insulin)
        bot.send_message(message.from_user.id, f'необходимо ввести примерно: {res} ед. инсулина /start либо /help');
    elif sugar < 5:
        r = float(sugar) / 5
        res = float(xe) / float(insulin)
        doza = float(res) - (1 - r)
        bot.send_message(message.from_user.id, f'необходимо ввести примерно: {doza} ед. инсулина /start либо /help');
    elif sugar > 8:
        r = float(sugar) - 8
        res = float(xe) / float(insulin)
        doza = float(res) + (r / fci)
        bot.send_message(message.from_user.id, f'необходимо ввести примерно: {doza} ед. инсулина /start либо /help');
    else:
        bot.send_message(message.from_user.id, 'введите пожалуйста цифрами')
        bot.register_next_step_handler(message, get_xe);


bot.infinity_polling()