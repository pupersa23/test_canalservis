# test_canalservis

Тестовое задание по работе с Google Spreadsheets

## Как запустить проект:

### Клонировать репозиторий и перейти в него в командной строке:

    git clone git@github.com:pupersa23/test_canalservis.git
    cd test_canalservis

### Cоздать и активировать виртуальное окружение:

    python -m venv env
    source env/bin/activate

### Установить зависимости из файла requirements.txt:

    python -m pip install --upgrade pip
    pip install -r requirements.txt

### Записать в переменные окружения (файл .env) необходимые ключи представленные в файле .env.exsmple:

    GOOGLEAPIJSON='' #Название файла для работы с GOOGLEAPI
    SHEETID='' #ID таблицы в Google spreadsheets
    DBNAME='' #Название основной БД в PostgresSQL
    DBNAME_2='' #Название БД с которой будут произвадится манипуляции в PostgresSQL
    USERNAME='' #Логин для доступа в PostgresSQL
    PASSWORD='' #Пароль для доступа в PostgresSQL
    HOST='' #IP для доступа в PostgresSQL

### Запустить проект:

    python sheets_test.py
    
Автор Владимир Рязанов - email ryazanov745@gmail.com
