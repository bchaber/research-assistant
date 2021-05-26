from dotenv import load_dotenv
load_dotenv()

from rq import Queue, Worker, Connection
from database import db
queue = Queue(connection=db)

def title(metadata):
  return metadata.get("title", "")
  
def authors(metadata):
  return ' and '.join([author.get("family") + ', ' + author.get("given")
  	for author in metadata.get("author", [])[:3]])

from tools import reader, finder
def parse_pdf_file(incoming):
  print("[*] processing new PDF file: " + incoming)
  doi = reader.extract_doi_from_file(incoming)
  if doi is None:
    return "[err] no DOI found in the provided stream"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  outgoing = '/outgoing/' + title(metadata) + " - " + authors(metadata) + ".pdf"
  print("[*] should move " + incoming + " to " + outgoing)
  if incoming != outgoing:
  	queue.enqueue("__main__.move_pdf", args=(incoming, outgoing))
  else:
    print("[_] no change for " + incoming)
  
def parse_pdf_stream(incoming, content):
  print("[*] processing new PDF stream: " + incoming)
  doi = reader.extract_doi_from_stream(content)
  if doi is None:
    return "[err] no DOI found in the provided stream"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  outgoing = '/outgoing/' + title(metadata) + " - " + authors(metadata) + ".pdf"
  if incoming != outgoing:
  	queue.enqueue("__main__.move_pdf", args=(incoming, outgoing))
  else:
    print("[_] no change for " + incoming)

def move_pdf(incoming, outgoing):
  print("[>] moving " + incoming + " to " + outgoing)
  os.rename(incoming, outgoing)

def add_pdf(newname, content):
  print("[x] would have add a PDF")
  pass

def add_bibitem(bibitem):
  print("[x] would have add bibitem")
  pass

def parse_citation(citation):
  print("[*] processing new citation:\n\t" + citation)
  doi = finder.find_doi(citation)
  if doi is None:
    return "[err] no DOI found in the provided free-form citation"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"
  queue.enqueue("__main__.add_bibitem", args=(bibitem,))

if __name__ == "__main__":
  with Connection(db):
    worker = Worker(queue)
    worker.work()
