# TODO:
# affected by the bug: https://github.com/ansible/ansible/issues/32499
from dotenv import load_dotenv
load_dotenv()

import os
DBXOUTGOING  = os.getenv("DBXOUTGOING")

from database import db
from local_worker import title, authors
from tools import reader, finder, scihub

def new_pdf(incoming, dropbox):
  print("[*] downloading " + incoming + " from Dropbox")
  _, f = dropbox.files_download(incoming)
  print("[*] extracting DOI from PDF stream")
  doi = reader.extract_doi_from_stream(f.content)
  if doi is None:
    return "[err] no DOI found in the provided stream"
  print("[*] finding metadata for DOI: " + doi)
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  outgoing = DBXOUTGOING + "/" + title(metadata) + " - " + authors(metadata) + ".pdf"
  if incoming != outgoing:
    print("[>] moving " + incoming + " to " + outgoing)
    dropbox.files_move(incoming, outgoing, autorename=True)

def new_citation(citation, dropbox):
  print("[*] finding DOI for new citation:\n> " + citation)
  doi = finder.find_doi(citation)
  if doi is None:
    return "[err] no DOI found in the provided free-form citation"
  print("[*] finding metadata for DOI: " + doi)
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"
  outgoing = DBXOUTGOING + "/" + title(metadata) + " - " + authors(metadata) + ".pdf"
  doi = metadata["DOI"]
  print("[v] fetching a PDF for DOI: " + doi)
  content = scihub.fetch_pdf(doi)
  print("[^] uploading the PDF to Dropbox: " + outgoing)
  dropbox.files_upload(content, outgoing)
