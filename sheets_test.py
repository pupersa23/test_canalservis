import datetime as dt
import logging
import os
import sys
import time

import gspread
import psycopg2
from dotenv import load_dotenv
from pycbrf import ExchangeRates

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(name)s, %(levelname)s, %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

load_dotenv()

GOOGLEAPIJSON = os.getenv('GOOGLEAPIJSON')
SHEETID = os.getenv('SHEETID')

DBNAME = os.getenv('DBNAME')
DBNAME_2 = os.getenv('DBNAME_2')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
TABLE_NAME = 'delivery'

RETRY_TIME = 30


def connect_to_maindb(value):
    """Выбор подключения к БД"""
    if value == DBNAME:
        conn = psycopg2.connect(
            dbname=DBNAME,
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
        )
    else:
        conn = psycopg2.connect(
            dbname=DBNAME_2,
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
        )
    return conn


def get_sheet():
    """Получение таблицы"""
    gc = gspread.service_account(
        filename=GOOGLEAPIJSON
    )
    sht1 = gc.open_by_key(SHEETID)
    worksheet = sht1.get_worksheet(0)
    list_of_dicts = worksheet.get_all_records()
    return list_of_dicts


def create_db():
    """Создание БД и добавление таблицы"""
    conn = connect_to_maindb(DBNAME)
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute(
        f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DBNAME_2}'"
    )
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {DBNAME_2}")
        logger.info('База данных создана')
        conn.close()

    conn_2 = connect_to_maindb(DBNAME_2)
    cursor = conn_2.cursor()
    conn_2.autocommit = True
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}
                (id INTEGER PRIMARY KEY,
                 order_number INTEGER,
                 price_dollar INTEGER,
                 price_ruble INTEGER,
                 date DATE)"""
    )
    logger.info('Таблица создана')
    cursor.close()
    conn_2.close()


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

        conn_2 = connect_to_maindb(DBNAME_2)
        cursor = conn_2.cursor()
        conn_2.autocommit = True
        cursor.execute(
            f"""INSERT INTO {TABLE_NAME}
            (id, order_number, price_dollar, price_ruble, date)
            VALUES ({list['№']},
                    {list['заказ №']},
                    {list['стоимость,$']},
                    {convert(list['стоимость,$'])},
                    '{newdate}'::date)"""
        )
        logger.info('Данные добавлены в БД')
        cursor.close()
        conn_2.close()


def delet_old_date():
    """Удаление старой таблицы"""
    conn_2 = connect_to_maindb(DBNAME_2)
    cursor = conn_2.cursor()
    conn_2.autocommit = True
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    logger.info('Таблица удалена')
    cursor.close()
    conn_2.close()


def main():
    """Основная работа программы"""
    logger.info('Программа запущен')
    current_timestamp = int(time.time())
    while True:
        try:
            delet_old_date()
            create_db()
            list_of_dicts = get_sheet()
            add_date(list_of_dicts)
        except Exception as error:
            current_timestamp = current_timestamp
            logger.info(f'Сбой в работе программы: {error}')
        else:
            current_timestamp = int(time.time())
        finally:
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
