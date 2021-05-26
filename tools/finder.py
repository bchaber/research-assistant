#!env python3
import requests, json
def find_metadata(doi):
  response = requests.get(f"http://dx.doi.org/{doi}",
                          headers={"Accept": "application/json"})
  if response.status_code != 200:
    print("[!] Invalid response code " + str(response.status_code) + ": ")
    print(response.content)
    return None, None
  metadata = json.loads(response.text)

  response = requests.get(f"http://dx.doi.org/{doi}",
                          headers={"Accept": "application/x-bibtex"})
  if response.status_code != 200:
    print("[!] Invalid response code " + str(response.status_code) + ": ")
    print(response.content)
    return None, None

  return metadata, response.text

from urllib.parse import quote
def find_doi(citation):
  citation = quote(citation)
  response = requests.get(f"https://api.crossref.org/works?query.bibliographic={citation}&rows=1")
  if response.status_code != 200:
    print("[!] Invalid response code " + str(response.status_code) + ": ")
    print(response.content)
    return None
  
  results = json.loads(response.text)
  if results.get('status') != 'ok':
    print("[!] Invalid status " + results.get('status'))
    return None

  for item in results['message']['items']:
    title  = item.get('title')[0]
    score  = item.get('score')
    doi    = item.get('DOI')
    return doi

from sys import argv, exit
if __name__ == '__main__':
  if len(argv) > 1:
    command = argv[1]
    if command == 'doi' and len(argv) > 2:
      metadata, bibitem = find_metadata(argv[2])
      print(bibitem)
      exit(0)
    if command == 'bib' and len(argv) > 2:
      doi = find_doi(argv[2])
      metadata, bibitem = find_metadata(doi)
      print(bibitem)
      exit(0)

  print("""\
finder doi [DOI] -- find metadata for a DOI
finder bib [citation] -- find metadata for a free-form citation\
        """)
