from flask import Flask, render_template, request, redirect
import csv
from translate import Translator
import requests
import hashlib
from PIL import Image, ImageFilter

app = Flask(__name__)  # Flask class uses to instantiate an app


@app.route('/')
# anytime we hit a slash/route,function hello_world is defined and returned Hello, World!'
def home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


def write_to_file(data):
    with open(file='./database.txt', mode='a') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        database.write(f'\n{email},{subject},{message}')


def write_to_csv(data):
    with open(file='./database.csv', mode='a') as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            return redirect('ThankYou.html')
        except:
            return 'did not save to database'
    else:
        return 'something went wrong.Try again!'


@app.route('/translate', methods=['POST', 'GET'])
def translate():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']
        translator = Translator(to_lang=language)
        translation = translator.translate(text)
        return render_template("translator.html", result=translation)


def request_api_data(query_char):
    url = 'https://api.pwnedpasswords.com/range/' + query_char
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(f'Error fetching:{res.status_code}, check the api and try again')
    return res


def get_password_leaks_count(hashes, hash_to_check):
    hashes = (line.split(':') for line in hashes.text.splitlines())
    for h, count in hashes:
        if h == hash_to_check:
            return count
    return 0


def pwned_api_check(password):
    # check password if it exists in api response
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first_five, tail = sha1password[:5], sha1password[5:]
    response = request_api_data(first_five)
    return get_password_leaks_count(response, tail)


@app.route('/pwned', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        password = request.form['password']
        count = pwned_api_check(password)
        return render_template('pwned.html', count=count, password=password)


@app.route('/ImageProcessing', methods=['POST', 'GET'])
def image_processing():
    if request.method == 'POST':
        f = request.files['image']
        f.save('./static/assets/images/'+f.filename)
        return render_template('ImageProcessing.html', file=f.filename)

