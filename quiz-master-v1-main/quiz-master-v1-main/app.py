from flask import Flask
app = Flask(__name__) 

app.secret_key='23f3003477'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import routes
import models

