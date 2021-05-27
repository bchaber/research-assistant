#!env python3
from bs4 import BeautifulSoup 
from requests import get

SCIHUB_URL = "https://sci-hub.se/"

def fetch_pdf(doi):
  response = get(SCIHUB_URL + doi)
  if response.status_code != 200:
    print("[!] Invalid response code " + str(response.status_code) + ":")
    print(response.content)
    return None

  soup = BeautifulSoup(response.content, "lxml")
  iframe = soup.find("iframe", attrs={"id":"pdf"})
  if iframe is None:
    print("[!] Couldn't find iframe in the Sci-hub's response")
    return None

  link = iframe["src"].split("#")[0]
  if link.startswith("//"):
    link = "https:" + link

  document = get(link)
  if document.headers["content-type"] != "application/pdf":
    print("[!] Invalid content type: " + document.headers["content-type"])
    return None

  return document.content

if __name__ == "__main__":
  from sys import argv
  content = fetch_pdf(argv[1])
  if content:
    print(content)
