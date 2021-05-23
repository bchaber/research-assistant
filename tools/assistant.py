import Dropbox
from flask import Flask
from redis import StrictRedis

app = Flask(__name__)
db  = StrictRedis(host='localhost', port=6379, db=0)

@app.route('/webhook', methods=['GET'])
def verify():
    resp = Response(request.args.get('challenge'))
    resp.headers['Content-Type'] = 'text/plain'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

from hashlib import sha256
import hmac
import threading

@app.route('/webhook', methods=['POST'])
def webhook():
    # Make sure this is a valid request from Dropbox
    signature = request.headers.get('X-Dropbox-Signature')
    if not hmac.compare_digest(signature, hmac.new(APP_SECRET, request.data, sha256).hexdigest()):
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

    dbx = Dropbox(token)
    has_more = True

    while has_more:
        if cursor is None:
            result = dbx.files_list_folder(path='')
        else:
            result = dbx.files_list_folder_continue(cursor)

        for entry in result.entries:
            # Ignore deleted files, folders, and non-markdown files
            if (isinstance(entry, DeletedMetadata) or
                isinstance(entry, FolderMetadata) or
                not entry.path_lower.endswith('.md')):
                continue

            # Convert to Markdown and store as <basename>.html
            _, resp = dbx.files_download(entry.path_lower)
            html = markdown(resp.content)
            dbx.files_upload(html, entry.path_lower[:-3] + '.html', mode=WriteMode('overwrite'))

        # Update cursor
        cursor = result.cursor
        db.hset('cursors', account, cursor)

        # Repeat only if there's more to do
        has_more = result.has_more
