import telebot
import requests
from pyairtable import Table


class Svyazka:
    def __init__(self, user_id):
        self.user_id = user_id
        self.usd = None
        self.won = None


svyzki_dict = {}
client = telebot.TeleBot('5630714715:AAEyHjpFNHdeHFTu-h5U3-JMSTs5BzMinEA')


def usd_krw_api() -> str:
    url = "https://openexchangerates.org/api/latest.json?app_id=b3aec8e91a634482b797a7e29bbd38f0&" \
          "symbols=KRW&prettyprint=true"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers).json()
    usdwon = response['rates']['KRW']
    return usdwon


@client.message_handler(commands=["run_auto"])
def run_auto(message):
    chat_id = message.chat.id
    table = Table('keySp0t9lDFoYBbEl', 'appXujWj3BOKy9GDm', 'USDKRW')
    last_record = table.first()
    usd = last_record['fields']['USD']
    krw = last_record['fields']['KRW']
    usdwon = int(usd_krw_api()) - 10
    client.send_message(message.chat.id, 'Щас все посчитаем!!!')
    client.send_message(message.chat.id, f'Для расчета будут использованые следующие курсы: \n'
                                         f'Курс 🇺🇸 (1$) - {str(usd)} руб.\n'
                                         f'Курс 🇰🇷 (1000₩) - {str(krw)} руб.\n'
                                         f'Курс USDKWR (XE 1$) - {str(usdwon)}₩')
    usd40 = int(round((40000 + 200) * usd, -3))  # 40.000$ если купить в ББР РУБ
    usd40_txt = '{0:,}'.format(usd40).replace(',', '.')  # форматированное представление рублей
    get_won_kor = round(40000 * usdwon, -3)  # примерное количесво ВОН по XE курсу
    won_kor_txt = '{0:,}'.format(get_won_kor).replace(',', '.')  # форматированное представление ВОН
    prim_rub_won = int(
        round((get_won_kor + 35000) * (krw / 1000), -3))  # полученое кол-во вон купить в рублях в Приморье
    prim_rub_txt = '{0:,}'.format(prim_rub_won).replace(',', '.')
    diff = usd40 - prim_rub_won  # разница в рублях в банках
    diff_frm = '{0:,}'.format(abs(diff)).replace(',', '.')
    if diff >= 0:
        diff_txt = f'Выгоднее в 🇰🇷 на {diff_frm}руб.'
    else:
        diff_txt = f'Выгоднее в 🇺🇸 на {diff_frm}руб.'
    text = f'40000$ в ББР - примерно {usd40_txt}руб.\n' \
           f'В Корее получат примерно {won_kor_txt}₩\n' \
           f'☝ эта же сумма в Приморье - {prim_rub_txt}руб.\n\n' \
           f'Итого: {diff_txt}'
    client.send_message(message.chat.id, text)


@client.message_handler(commands=["run"])
def run(message):
    chat_id = message.chat.id
    msg = client.send_message(message.chat.id, 'Для расчета выгоды введите курс доллара 🇺🇸 и воны 🇰🇷. '
                                               'Каждая валюта с новой строки ↩'
                                               '\n\nКурс доллара 🇺🇸 (например 62.90):')
    svyzki_dict[chat_id] = Svyazka(user_id=chat_id)
    client.register_next_step_handler(msg, user_unswer)


def user_unswer(message):
    if str(message.text).lower() == 'выход':
        return None
    try:
        user_id = message.chat.id
        svyazka = svyzki_dict[user_id]
        svyazka.usd = float(message.text)
        msg = client.send_message(message.chat.id, 'Курс воны 🇰🇷 (например 45.70):')
        client.register_next_step_handler(msg, calc_unswer)
    except Exception as e:
        client.send_message(message.chat.id, 'Скорее всего ошибка ввода курса валюты. Ввведите в верном формате. '
                                             'Например: 62.90 (разделитель точка) \n'
                                             'Начните все сначала.')


def calc_unswer(message):
    try:
        user_id = message.chat.id
        svyazka = svyzki_dict[user_id]
        svyazka.won = float(message.text)
        client.send_message(message.chat.id, 'Щас все посчитаем!')
        usdwon = usd_krw_api()  # курс обмена доллар-вона по API
        usd40 = int(round((40000 + 200) * svyazka.usd, -3))  # 40.000$ если купить в ББР  РУБ
        usd40_txt = '{0:,}'.format(usd40).replace(',', '.')  # форматированное представление рублей
        get_won_kor = round(40000 * (int(usdwon) - 10), -3) # примерное количесво ВОН по XE курсу
        won_kor_txt = '{0:,}'.format(get_won_kor).replace(',', '.')  # форматированное представление ВОН
        prim_rub_won = int(round((get_won_kor + 35000) * (svyazka.won / 1000), -3)) # полученое кол-во вон купить в рублях в Приморье
        prim_rub_txt = '{0:,}'.format(prim_rub_won).replace(',', '.')
        diff = usd40 - prim_rub_won # разница в рублях в банках
        diff_frm = '{0:,}'.format(abs(diff)).replace(',', '.')
        if diff >= 0:
            diff_txt = f'Выгоднее в 🇰🇷 на {diff_frm}руб.'
        else:
            diff_txt = f'Выгоднее в 🇺🇸 на {diff_frm}руб.'
        text = f'Расчеты произведены исходя из курсов валют:\n' \
               f'Курс доллара 🇺🇸: {svyazka.usd}руб.\n' \
               f'Курс воны 🇰🇷 (1000): {svyazka.won}руб.\n' \
               f'Курс USDKRW (XE) 1$: {round(float(usdwon))}₩\n' \
               f'40000$ в ББР - примерно {usd40_txt}руб.\n' \
               f'В Корее получат примерно {won_kor_txt}₩\n' \
               f'☝ эта же сумма в Приморее - {prim_rub_txt}руб.\n\n' \
               f'Итого: {diff_txt}'

        client.send_message(message.chat.id, text)
    except Exception as e:
        client.reply_to(message, 'Ошибочка вышла!!!!')


client.polling()
