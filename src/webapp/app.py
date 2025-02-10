from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from .api import api
import os

app = Flask(__name__)
CORS(app)  # Включаем CORS для API

# Регистрируем API blueprint
app.register_blueprint(api)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 