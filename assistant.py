from flask import Flask
from redis import StrictRedis

from dotenv import load_dotenv
load_dotenv()

import os, random, string
REDISHOST = os.getenv("REDISHOST")
PDFINCOMING = os.getenv("PDFINCOMING")
PDFOUTGOING = os.getenv("PDFOUTGOING")
SESSIONKEY  = os.getenv("SESSIONKEY")

app = Flask(__name__)
db  = StrictRedis(host=REDISHOST, port=6379, db=0)

from dropbox_integration import dbx
from zotero_integration  import zot
app.register_blueprint(dbx)
app.register_blueprint(zot)

from tools import reader, finder
@app.route("/new-pdf/<filename>", methods=["GET"])
def new_pdf(filename):
  doi = reader.extract_doi(filename)

@app.route("/new-citation", methods=["POST"])
def new_citation():
  citation = request.args.get("citation")
  doi = finder.find_doi(citation)
  metadata, bibitem = finder.find_metadata(doi)

if __name__ == "__main__":
  print("Your session key is " + SESSIONKEY)
  print(app.url_map)
  app.run()
