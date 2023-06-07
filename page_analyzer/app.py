from flask import (
    Flask,
    flash,
    request,
    get_flashed_messages,
    render_template,
    redirect,
    url_for
)
import os
import datetime
import validators
from dotenv import load_dotenv
import psycopg2
from psycopg2 import extras
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY)
DATABASE_URL = os.getenv('DATABASE_URL')


@app.get('/')
def index():
    # messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        # messages=messages,
    )


@app.get('/urls')
def get_urls():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM urls ORDER BY id DESC')
                result = cur.fetchall()
                #  print(result) scheme: [(47, 'https://autoreview.ru', datetime.date(2023, 6, 5)), ...]
    except psycopg2.Error:
        return None
    finally:
        conn.close()
    return render_template(
        'urls/urls.html',
        data=result
        # checks=result['checks'],
        # codes=result['status_codes']
    )


@app.post('/urls')
def post_url():
    url = request.form.to_dict().get('url')  # e.g. https://www.avito.ru/
    error_messages = list()
    if validate(url):
        for message in validate(url):
            flash(message)
        error_messages.extend(validate(url))
        return render_template(
            'index.html',
            error_messages=error_messages,
        )
    created_at = datetime.datetime.now().date()
    parsed_url = urlparse(url)
    name = parsed_url[0] + '://' + parsed_url[1]
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id FROM urls WHERE name = %s LIMIT 1',
                    (name,)
                )
                data = cur.fetchone()
                # print('DATA: ', data)
                if data:
                    flash('Страница уже существует', 'info')
                    return redirect(url_for('get_url', id=data[0]))
                cur.execute('''
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s) RETURNING id;
                    ''',
                    (name, created_at))
                url_id = cur.fetchone()[0]
                # print('URL_ID: ', url_id)
                flash('Страница успешно добавлена', 'success')
    except psycopg2.Error:
        return None
    finally:
        conn.close()

    return redirect(url_for('get_url', id=url_id))
    # return render_template(
    #     'urls/urls_id.html',
    #     data=data,
    #     url_id=url_id
    # )


@app.get('/urls/<int:id>')
def get_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
                cur.execute(
                    'SELECT id, name, created_at FROM urls WHERE id = %s LIMIT 1',
                    (id,)
                )
                result = cur.fetchone()
                # print(result)  (7, 'https://www.avito.ru', datetime.date(2023, 6, 6))
                cur.execute(
                    'SELECT id, url_id, status_code, h1, title, description, created_at FROM url_checks WHERE url_id = %s ORDER BY id DESC',
                    (id,)
                )
                checks = cur.fetchall()
                # print(checks):  [Record(id=27, url_id=11, created_at=datetime.date(2023, 6, 7)), ...]
                # print(check.id):  27
    except psycopg2.Error:
        return None
    finally:
        conn.close()
    return render_template(
                    'urls/urls_id.html',
                    result=result,
                    checks=checks
                )


@app.post('/urls/<int:id>')
def url_checks(id):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor(
                cursor_factory=extras.NamedTupleCursor
            ) as cur:
                cur.execute(
                    'SELECT id, name, created_at FROM urls WHERE id = %s LIMIT 1',
                    (id,)
                )
                url  = cur.fetchone().name
                # print(url):  e.g. https://www.avito.ru
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                except requests.exceptions.RequestException as error:
                    flash('Произошла ошибка при проверке', 'danger')
                    return redirect(url_for('get_url', id=id))
                
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string
                h1 = soup.h1.string
                desc = soup.find("meta", property='og:description')
                desc_content = desc.get("content")
                print(desc_content)

                cur.execute('''
                    INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) values
                    (%s, %s, %s, %s, %s, %s)
                    ''',
                    (id, response.status_code, h1, title, desc_content, datetime.datetime.now().date(),)
                )
                flash('Страница успешно проверена', 'success')
            conn.commit()
    except psycopg2.Error:
        return None
    finally:
        conn.close()
    return redirect(url_for('get_url', id=id))


def validate(url_from_request):
    errors = list()
    if len(url_from_request) > 255:
        errors.append('URL превышает 255 символов')
    if not validators.url(url_from_request):
        errors.append('Некорректный URL')
    if not url_from_request:
        errors.append('URL обязателен')
    return errors
