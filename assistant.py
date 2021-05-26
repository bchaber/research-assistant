from flask import Flask 
from dotenv import load_dotenv
load_dotenv()

import os, random, string
SESSIONKEY  = os.getenv("SESSIONKEY")

app = Flask(__name__)

from rq import Queue
from database import db
from dropbox_integration import dbx
from zotero_integration  import zot
app.register_blueprint(dbx)
app.register_blueprint(zot)
queue = Queue(connection=db)

from flask import request, render_template, abort
@app.route("/")
def home():
  return render_template("home.html")

from urllib.parse import quote, unquote
@app.route("/new-pdf/<path:filename>", methods=["GET"])
def new_pdf(filename):
  job = queue.enqueue("__main__.parse_pdf_file", '/' + unquote(filename))
  return job.id

@app.route("/new-citation", methods=["POST"])
def new_citation():
  citation = request.form.get("citation")
  if citation is None:
    abort(403)
  job = queue.enqueue("__main__.parse_citation", args=(citation,))
  return job.id

if __name__ == "__main__":
  print("[@] Your session key is " + SESSIONKEY)
  print(app.url_map)
  app.run()
