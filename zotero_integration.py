from flask import Blueprint

import os
ZOTEROKEY = os.getenv("ZOTEROKEY")

zot = Blueprint("zotero", __name__, template_folder="templates")
