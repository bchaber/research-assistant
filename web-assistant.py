from flask import Flask 
from dotenv import load_dotenv
load_dotenv()

import os
SESSIONKEY = os.getenv("SESSIONKEY")
SECRETKEY  = os.getenv("SECRETKEY")
app = Flask(__name__)
app.secret_key = SECRETKEY

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
  if not os.getenv("ZOTAPIKEY"):
    print("[?] Unknown value of ZOTAPIKEY")
  if not os.getenv("ZOTUSERID"):
    print("[?] Unknown value of ZOTUSERID")
  if not os.getenv("ZOTGROUP"):
    print("[?] Unknown value of ZOTGROUP")
  if not os.getenv("DBXACCOUNT"):
    print("[?] Unknown value of DBXACCOUNT")
  if not os.getenv("DBXSECRET"):
    print("[?] Unknown value of DBXSECRET")
  if not os.getenv("DBXINCOMING"):
    print("[?] Unknown value of DBXINCOMING")
  if not os.getenv("DBXOUTGOING"):
    print("[?] Unknown value of DBXOUTGOING")
  if not os.getenv("REDISHOST"):
    print("[?] Unknown value of REDISHOST")
  if not os.getenv("REDISPORT"):
    print("[?] Unknown value of REDISPORT")
  if not os.getenv("REDISAUTH"):
    print("[?] Unknown value of REDISAUTH")
  app.run()
