# Based on an example from https://www.dropbox.com/developers/reference/webhooks
from flask import Flask
from redis import StrictRedis

from dotenv import load_dotenv
load_dotenv()

import os
REDISHOST = os.getenv("REDISHOST")
SECRETKEY = os.getenv("SECRETKEY")
ZOTEROKEY = os.getenv("ZOTEROKEY")
PDFINCOMING = os.getenv("PDFINCOMING")
PDFOUTGOING = os.getenv("PDFOUTGOING")

app = Flask(__name__)
db  = StrictRedis(host=REDISHOST, port=6379, db=0)

from dropbox_interaction import dbx
from zotero_integration  import zot

if __name__ == "__main__":
  app.run()
