from pyzotero.zotero import Zotero

import os
ZOTAPIKEY = os.getenv("ZOTAPIKEY")
ZOTUSERID = os.getenv("ZOTUSERID")
ZOTGROUP  = os.getenv("ZOTGROUP")

def save_bibitem(metadata):
  zotero = Zotero(ZOTGROUP, 'group', ZOTAPIKEY)
  template = None
  
  if metadata['type'] == 'article-journal':
    template = zotero.item_template('journalArticle')
    update_article(template, metadata)
  if metadata['type'] == 'paper-conference':
    template = zotero.item_template('conferencePaper')
    update_conference(template, metadata)

  if template:
    print("[>] Saving " + metadata['type'] + " to Zotero group #" + ZOTGROUP)
    zotero.create_items([template])

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