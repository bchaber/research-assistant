from dotenv import load_dotenv
load_dotenv()

import os
PDFOUTGOING  = os.getenv("PDFOUTGOING")
if not PDFOUTGOING:
  print("[?] Unknown value of PDFOUTGOING")

from tools import reader, finder, scihub

def title(metadata):
  return metadata.get("title", "")
  
def authors(metadata):
  return ' and '.join([author.get("family") + ', ' + author.get("given")
  	for author in metadata.get("author", [])[:3]])

def new_pdf(incoming):
  print("[*] extracting DOI from PDF file: " + incoming)
  doi = reader.extract_doi_from_file(incoming)
  if doi is None:
    return "[err] no DOI found in the provided file"
  print("[*] finding metadata for DOI: " + doi)
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  outgoing = PDFOUTGOING + "/" + title(metadata) + " - " + authors(metadata) + ".pdf"
  if incoming != outgoing:
    print("[>] moving " + incoming + " to " + outgoing)
    os.rename(incoming, outgoing)

def new_citation(citation):
  print("[*] finding DOI for new citation:\n> " + citation)
  doi = finder.find_doi(citation)
  if doi is None:
    return "[err] no DOI found in the provided free-form citation"
  print("[*] finding metadata for DOI: " + doi)
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"
  outgoing = PDFOUTGOING + "/" + title(metadata) + " - " + authors(metadata) + ".pdf"
  doi = metadata["DOI"]
  print("[v] fetching a PDF for DOI: " + doi)
  content = scihub.fetch_pdf(doi)
  print("[^] uploading the PDF to Dropbox: " + outgoing)
  with open(outgoing, "wb") as f:
    f.write(content)
