#!env python3
import re
regex = re.compile("(?P<doi>10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)

import fitz

def extract_doi(docs):
  for page in docs:
    if page.number > 2:
      break
    txt = page.getText()
    doi = re.search(regex, txt)
    if doi:
      return doi.group("doi")
  return None

def extract_doi_from_file(pdf_file):
  with fitz.open(pdf_file) as docs:
    return extract_doi(docs)
  return None

def extract_doi_from_stream(pdf_stream):
  with fitz.open(stream=pdf_stream, filetype="pdf") as docs:
    return extract_doi(docs)
  return None

from sys import argv, exit
if __name__ == '__main__':
  if len(argv) > 1:
    doi = extract_doi_from_file(argv[1])
    if doi:
      print(f"[+] Found DOI: {doi}")
      exit(0)
    else:
      print("[!] Couldn't find DOI")
      exit(1)

  print("""\
reader [PDF file]\
        """)
