# TODO:
# affected by the bug: https://github.com/ansible/ansible/issues/32499
from dotenv import load_dotenv
load_dotenv()

from sys import argv
from rq import Queue, Worker, Connection
from database import db
name = 'default' if len(argv) < 2 else argv[1]
queue = Queue(name, connection=db)

from local_worker import title, authors
from tools import reader, finder, scihub
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
  #if incoming != outgoing:
  #	queue.enqueue("__main__.move_pdf", args=(incoming, outgoing))
  #else:
  #  print("[_] no change for " + incoming)
  
def parse_pdf_stream(incoming, content, dropbox):
  print("[*] processing new PDF stream: " + incoming)
  doi = reader.extract_doi_from_stream(content)
  if doi is None:
    return "[err] no DOI found in the provided stream"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "[err] error while finding metadata"

  outgoing = '/outgoing/' + title(metadata) + " - " + authors(metadata) + ".pdf"
  if incoming != outgoing:
  	queue.enqueue("__main__.move_pdf", args=(incoming, outgoing, dropbox))
  else:
    print("[_] no change for " + incoming)

def move_pdf(incoming, outgoing, dropbox):
  print("[>] moving " + incoming + " to " + outgoing)
  dropbox.files_move(incoming, outgoing, autorename=True)

def add_pdf(metadata, dropbox):
  outgoing = '/tmp/outgoing/' + title(metadata) + " - " + authors(metadata) + ".pdf"
  print("[v] adding " + outgoing)
  doi = metadata.get("DOI")
  if doi:
    print("[v] fetching a PDF for " + doi)
    content = scihub.fetch_pdf(doi)
    #dropbox.files_upload(content, outgoing)
    with open(outgoing, "wb") as f:
      f.write(content)

def add_bibitem(bibitem):
  print("[x] should add the bibitem:")
  print(bibitem)
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
  queue.enqueue("__main__.add_pdf", args=(metadata, 0))

if __name__ == "__main__":
  with Connection(db):
    worker = Worker(queue)
    worker.work()
