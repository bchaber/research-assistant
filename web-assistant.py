from flask import Flask 
from dotenv import load_dotenv
load_dotenv()

import os
SESSIONKEY  = os.getenv("SESSIONKEY")

app = Flask(__name__)

from rq import Queue
from database import db
#from onedrive_integration import one
from dropbox_integration  import dbx
from zotero_integration   import zot
#app.register_blueprint(one)
app.register_blueprint(dbx)
app.register_blueprint(zot)

from flask import request, render_template, abort
@app.route("/")
def home():
  return render_template("home.html")

if __name__ == "__main__":
  print("[@] Your session key is " + SESSIONKEY)
  app.run()
