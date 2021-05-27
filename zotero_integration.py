from flask import Blueprint
from flask import request, abort, flash, redirect

zot = Blueprint("zotero", __name__, template_folder="templates")

import threading
@zot.route('/save', methods=['POST'])
def webhook():
  metadata = request.json
  if metadata['type'] not in ['article-journal', 'paper-conference']:
    abort(403)

  threading.Thread(target=process_metadata, args=(metadata,)).start()
  flash('I am on it!')
  return redirect('/')

from zotero_worker import save_bibitem
def process_metadata(metadata):
  save_bibitem(metadata)