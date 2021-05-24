# Based on an example from https://www.dropbox.com/developers/reference/webhooks
from dropbox import Dropbox
from flask import Blueprint, Response
from flask import request, abort

import os, json, threading
APPSECRET = os.getenv("APPSECRET").encode()

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
    if not hmac.compare_digest(signature, hmac.new(APPSECRET, request.data, sha256).hexdigest()):
        abort(403)

    for account in json.loads(request.data)['list_folder']['accounts']:
        # We need to respond quickly to the webhook request, so we do the
        # actual work in a separate thread. For more robustness, it's a
        # good idea to add the work to a reliable queue and process the queue
        # in a worker process.
        threading.Thread(target=process_user, args=(account,)).start()
    return ''

def process_user(account):
    # OAuth token for the user
    token = db.hget('tokens', account)
    # cursor for the user (None the first time)
    cursor = db.hget('cursors', account)

    dropbox = Dropbox(token)
    has_more = True

    while has_more:
        if cursor is None:
            result = dropbox.files_list_folder(path='')
        else:
            result = dropbox.files_list_folder_continue(cursor)

        for entry in result.entries:
            # Ignore deleted files, folders, and non-markdown files
            if (isinstance(entry, DeletedMetadata) or
                isinstance(entry, FolderMetadata) or
                not entry.path_lower.endswith('.pdf')):
                continue

            incoming = entry.path_lower
            _, resp = dropbox.files_download(incoming)
            outgoing = process_pdf(incoming)
            dropbox.files_move(incoming, outgoing, autorename=True)

        # Update cursor
        cursor = result.cursor
        db.hset('cursors', account, cursor)

        # Repeat only if there's more to do
        has_more = result.has_more

def title(metadata):
  return metadata.get("title", "")
def authors(metadata):
  return ' and '.join([author.get("family") + ", " + author.get("given") for author in metadata.get("author", [])[:3]])

def process_pdf(filename):
  print("Processing new PDF: " + filename)
  doi = reader.extract_doi('/' + filename)
  if doi is None:
    return "No DOI found in the provided file"
  metadata, bibitem = finder.find_metadata(doi)
  if metadata is None:
    return "Error while finding metadata"
  title = metadata.get("title")
  authors = metadata.get("author")

  return authors(metadata) + " - " + title(metadata) + ".pdf"