from flask import Flask 
from dotenv import load_dotenv
load_dotenv()

import os, random, string
SESSIONKEY  = os.getenv("SESSIONKEY")
PDFINCOMING = os.getenv("PDFINCOMING")
PDFOUTGOING = os.getenv("PDFOUTGOING")

app = Flask(__name__)

from database import db
from dropbox_integration import dbx
from zotero_integration  import zot
app.register_blueprint(dbx)
app.register_blueprint(zot)

from flask import request, render_template, abort
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
  incoming = '/' + filename
  print("[*] processing new PDF file: " + incoming)
  doi = reader.extract_doi_from_file(incoming)
  if doi is None:
    return "[err] no DOI found in the provided file"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  outgoing = PDFOUTGOING + '/' + title(metadata) + " - " + authors(metadata) + ".pdf"
  print("[>] moving " + incoming + " to " + outgoing)
  os.rename(incoming, outgoing)
  return outgoing

@app.route("/new-citation", methods=["POST"])
def new_citation():
  citation = request.form.get("citation")
  if citation is None:
      abort(403)
  print("[*] processing new citation:\n\t" + citation)
  doi = finder.find_doi(citation)
  if doi is None:
    return "[err] no DOI found in the provided free-form citation"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  return bibitem

if __name__ == "__main__":
  print("[@] Your session key is " + SESSIONKEY)
  print(app.url_map)
  app.run()
