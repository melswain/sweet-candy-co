from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

@app.route('/')
def index():
    # placeholder data for fridge temperature and humidity values
    fridge_data = [
        {'name': 'Fridge 1', 'humidity': '45%', 'temperature': '4°C'},
        {'name': 'Fridge 2', 'humidity': '50%', 'temperature': '5°C'}
    ]
    return render_template('index.html', fridges=fridge_data)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    flash(f'Added {name} ({email}, {phone}) successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)