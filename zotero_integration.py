from pyzotero.zotero import Zotero
from flask import Blueprint
from flask import request, abort

import os
ZOTAPIKEY = os.getenv("ZOTAPIKEY")
ZOTUSERID = os.getenv("ZOTUSERID")
ZOTGROUP  = os.getenv("ZOTGROUP")
if not ZOTAPIKEY:
  print("[?] Unknown value of ZOTAPIKEY")
if not ZOTUSERID:
  print("[?] Unknown value of ZOTUSERID")
if not ZOTGROUP:
  print("[?] Unknown value of ZOTGROUP")

zot = Blueprint("zotero", __name__, template_folder="templates")

@zot.route('/save', methods=['POST'])
def save_citation():
  zotero = Zotero(ZOTGROUP, 'group', ZOTAPIKEY)
  metadata = request.json

  if metadata['type'] == 'article-journal':
    template = zotero.item_template('journalArticle')
    update_article(template, metadata)
  if metadata['type'] == 'paper-conference':
    template = zotero.item_template('conferencePaper')
    update_conference(template, metadata)
  if metadata['type'] not in ['article-journal', 'paper-conference']:
  	abort(403)

  print("[*] Saving a/an " + metadata['type'] + " to Zotero group #" + ZOTGROUP)
  response = zotero.create_items([template])
  return str(response)

def update_authors(item, json):
  item['creators'] = []
  for author in json['author']:
    item['creators'].append({
    	'creatorType':'author', 
        'firstName': author['given'],
        'lastName': author['family']})

def update_article(item, json):
  update_authors(item, json)
  item['title'] = json['title']
  item['volume']= json['volume']
  item['issue'] = json['issue']
  item['pages'] = json['page']
  item['DOI']   = json['DOI']
  item['language'] = json['language']
  item['publicationTitle'] = json['publisher']

def update_conference(item, json):
  update_authors(item, json)
  item['title'] = json['title']
  item['DOI']   = json['DOI']
  item['publisher'] = json['publisher']
  item['conferenceName'] = json['event']