import datetime as dt
import os

import gspread
import psycopg2
from dotenv import load_dotenv
from pycbrf import ExchangeRates

load_dotenv()

GOOGLEAPIJSON = os.getenv('GOOGLEAPIJSON')
SHEETID = os.getenv('SHEETID')
DBNAME = os.getenv('DBNAME')
USER_B = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')


def get_sheet():
    """Получение таблицы"""
    gc = gspread.service_account(
        filename=GOOGLEAPIJSON
    )
    sht1 = gc.open_by_key(SHEETID)
    worksheet = sht1.get_worksheet(0)
    list_of_dicts = worksheet.get_all_records()
    return list_of_dicts


def convert(value):
    """Конвертирование согласно ЦБ в рубли"""
    todaydate = dt.date.today()
    rates = ExchangeRates(todaydate, locale_en=True)
    rubl_convert = value * rates['USD'].value
    return rubl_convert


def add_date(value):
    """Добавление данных в базу"""
    for list in value:
        date1 = list['срок поставки']
        new_date = dt.datetime.strptime(date1, "%d.%m.%Y")
        newdate = new_date.strftime("%Y-%m-%d")

        conn = psycopg2.connect(
            dbname=DBNAME,
            user=USER_B,
            password=PASSWORD,
            host=HOST,
        )
        cursor = conn.cursor()
        conn.autocommit = True
        cursor.execute(
            f"""INSERT INTO delivery
            (id, order_number, price_dollar, price_ruble, date)
            VALUES ({list['№']},
                    {list['заказ №']},
                    {list['стоимость,$']},
                    {convert(list['стоимость,$'])},
                    '{newdate}'::date)"""
        )
        cursor.close()
        conn.close()


if __name__ == "__main__":
    list_of_dicts = get_sheet()
    add_date(list_of_dicts)
