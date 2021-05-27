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
  for author in json.get('author', []):
    item['creators'].append({
    	'creatorType':'author', 
        'firstName': author.get('given'),
        'lastName': author.get('family')
        })

def update_article(item, json):
  update_authors(item, json)
  item['title'] = json.get('title')
  item['volume']= json.get('volume')
  item['issue'] = json.get('issue')
  item['pages'] = json.get('page')
  item['DOI']   = json.get('DOI')
  item['language'] = json.get('language')
  item['publicationTitle'] = json.get('publisher')

def update_conference(item, json):
  update_authors(item, json)
  item['title'] = json.get('title')
  item['DOI']   = json.get('DOI')
  item['publisher'] = json.get('publisher')
  item['conferenceName'] = json.get('event')