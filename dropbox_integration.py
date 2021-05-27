from database import db

# Based on an example from https://www.dropbox.com/developers/reference/webhooks
from dropbox import Dropbox
from flask import Blueprint, Response
from flask import request, abort

import os, json, threading
DBXACCOUNT = os.getenv("DBXACCOUNT")
DBXSECRET = os.getenv("DBXSECRET")
DBXINCOMING  = os.getenv("DBXINCOMING")

dbx = Blueprint("dropbox", __name__, template_folder="templates")
@dbx.route('/webhook', methods=['GET'])
def verify():
    resp = Response(request.args.get('challenge'))
    resp.headers['Content-Type'] = 'text/plain'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

from hashlib import sha256
import hmac
import threading
@dbx.route('/webhook', methods=['POST'])
def webhook():
    # Make sure this is a valid request from Dropbox
    signature = request.headers.get('X-Dropbox-Signature')
    if not hmac.compare_digest(signature, hmac.new(DBXSECRET.encode(), request.data, sha256).hexdigest()):
        abort(403)

    for account in json.loads(request.data)['list_folder']['accounts']:
        # We need to respond quickly to the webhook request, so we do the
        # actual work in a separate thread. For more robustness, it's a
        # good idea to add the work to a reliable queue and process the queue
        # in a worker process.
        threading.Thread(target=process_pdfs, args=(account,)).start()
    return ''

@dbx.route('/cite', methods=['POST'])
def cite():
    citation = request.form.get("citation")
    if citation is None:
      abort(403)
    
    account  = DBXACCOUNT
    threading.Thread(target=process_citation, args=(account, citation)).start()
    return ''

from dropbox.files import DeletedMetadata, FolderMetadata
from dropbox_worker import new_pdf, new_citation
def process_pdfs(account):
    token = db.hget('tokens', account).decode()
    cursor = db.hget('cursors', account).decode()
    dropbox = Dropbox(token)
    has_more = True

    while has_more:
        if cursor is None:
            result = dropbox.files_list_folder(path=DBXINCOMING)
        else:
            result = dropbox.files_list_folder_continue(cursor)

        for entry in result.entries:
            # Ignore deleted files, folders
            if (isinstance(entry, DeletedMetadata) or
                isinstance(entry, FolderMetadata) or
                not entry.path_lower.endswith('.pdf')):
                print("[~] skip " + entry.path_lower)
                continue
            new_pdf(entry.path_lower, dropbox)

        # Update cursor
        cursor = result.cursor
        db.hset('cursors', account, cursor)

        # Repeat only if there's more to do
        has_more = result.has_more

def process_citation(account, citation):
    token = db.hget('tokens', account).decode()
    cursor = db.hget('cursors', account).decode()
    dropbox = Dropbox(token)
    metadata = new_citation(citation, dropbox)
    requests.post()