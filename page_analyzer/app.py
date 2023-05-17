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
from urllib.parse import urlparse


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


@app.post('/')
def get_url():
    url = request.form.to_dict().get('url')
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
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS urls (
                    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    name varchar(255),
                    created_at date
                );''')
                cur.execute(
                    'SELECT id FROM urls WHERE name = %s LIMIT 1',
                    (name,)
                )
                data = cur.fetchone()
                if data:
                    flash('Страница уже существует', 'info')
                    return data[0]
                cur.execute('''
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s) RETURNING id;
                    ''',
                    (name, created_at))
                url_id = cur.fetchone()[0]
                flash('Страница успешно добавлена', 'success')
    except psycopg2.Error:
        return None
    finally:
        conn.close()

    return render_template(
        'show.html',
        data=data,
        url_id=url_id
    )



@app.route('/urls/<id>')
def show_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls;')
    websites = cur.fetchall()
    cur.close()
    conn.close()
    id = websites[0][0]
    website_name = websites[0][1]
    creation_date = websites[0][2]
    return render_template(
        'show.html',
        success_message=success_message,
        id=id,
        website_name=website_name,
        creation_date=creation_date
    )
    


def validate(url_from_request):
    errors = list()
    if len(url_from_request) > 255:
        errors.append('URL превышает 255 символов')
    if not validators.url(url_from_request):
        errors.append('Некорректный URL')
    if not url_from_request:
        errors.append('URL обязателен')
    return errors
