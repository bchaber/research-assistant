from flask import Flask 
from redis import StrictRedis

from dotenv import load_dotenv
load_dotenv()

import os, random, string
REDISHOST = os.getenv("REDISHOST")
REDISPORT = os.getenv("REDISPORT")
REDISAUTH = os.getenv("REDISAUTH")
SESSIONKEY  = os.getenv("SESSIONKEY")
PDFINCOMING = os.getenv("PDFINCOMING")
PDFOUTGOING = os.getenv("PDFOUTGOING")

app = Flask(__name__)
db  = StrictRedis(host=REDISHOST, port=REDISPORT, password=REDISAUTH, db=0)

from dropbox_integration import dbx
from zotero_integration  import zot
app.register_blueprint(dbx)
app.register_blueprint(zot)

from flask import request, render_template
@app.route("/")
def home():
  return render_template("home.html")

def title(metadata):
  return metadata.get("title", "")
def authors(metadata):
  return ' and '.join([author.get("family") + ", " + author.get("given") for author in metadata.get("author", [])[:3]])

from tools import reader, finder
@app.route("/new-pdf/<path:filename>", methods=["GET"])
def new_pdf(filename):
  print("Processing new PDF: " + filename)
  doi = reader.extract_doi('/' + filename)
  if doi is None:
    return "No DOI found in the provided file"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "Error while finding metadata"

  return authors(metadata) + " - " + title(metadata) + ".pdf"

@app.route("/new-citation", methods=["POST"])
def new_citation():
  citation = request.form.get("citation")
  if citation is None:
    return "No citation"
  print("Processing new citation: " + citation)
  doi = finder.find_doi(citation)
  if doi is None:
    return "No DOI found in the provided free-form citation"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "Error while finding metadata"

  return bibitem

if __name__ == "__main__":
  print("Your session key is " + SESSIONKEY)
  print(app.url_map)
  app.run()
