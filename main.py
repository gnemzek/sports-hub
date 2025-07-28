from dotenv import load_dotenv
import os
from flask import Flask, render_template

load_dotenv
api_key = os.getenv("SPORTS_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')