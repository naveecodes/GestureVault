from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
from datetime import datetime, timezone
import sqlite3, base64, re

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
PHOTOS = DATA / 'intruder_photos'
DATA.mkdir(exist_ok=True)
PHOTOS.mkdir(exist_ok=True)
DB = DATA / 'security.db'
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            result TEXT NOT NULL,
            sequence TEXT NOT NULL,
            reason TEXT,
            photo_path TEXT
        )''')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/status')
def status():
    with connect() as db:
        total = db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]
        denied = db.execute("SELECT COUNT(*) FROM attempts WHERE result='DENIED'").fetchone()[0]
        granted = db.execute("SELECT COUNT(*) FROM attempts WHERE result='GRANTED'").fetchone()[0]
        rows = db.execute('SELECT id,timestamp,result,sequence,reason,photo_path FROM attempts ORDER BY id DESC LIMIT 12').fetchall()
    return jsonify({'total': total, 'denied': denied, 'granted': granted, 'events': [dict(r) for r in rows]})


@app.post('/api/attempt')
def attempt():
    payload = request.get_json(silent=True) or {}
    result = 'GRANTED' if payload.get('result') == 'GRANTED' else 'DENIED'
    sequence = str(payload.get('sequence', ''))[:200]
    reason = str(payload.get('reason', ''))[:200]
    photo_path = None
    image_data = payload.get('photo')
    if result == 'DENIED' and isinstance(image_data, str) and image_data.startswith('data:image/jpeg;base64,'):
        try:
            raw = base64.b64decode(image_data.split(',', 1)[1], validate=True)
            if len(raw) <= 4 * 1024 * 1024:
                filename = datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.jpg'
                (PHOTOS / filename).write_bytes(raw)
                photo_path = filename
        except (ValueError, OSError):
            pass
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
    with connect() as db:
        cur = db.execute('INSERT INTO attempts(timestamp,result,sequence,reason,photo_path) VALUES(?,?,?,?,?)',
                         (timestamp, result, sequence, reason, photo_path))
        event_id = cur.lastrowid
    return jsonify({'ok': True, 'id': event_id, 'timestamp': timestamp, 'photo_saved': bool(photo_path)}), 201


@app.get('/photos/<path:filename>')
def photos(filename):
    # Photos are served only through this local demonstration app. Do not expose this server publicly without authentication.
    if not re.fullmatch(r'[0-9_]+\.jpg', filename):
        return ('Not found', 404)
    return send_from_directory(PHOTOS, filename, mimetype='image/jpeg')


@app.post('/api/reset-demo')
def reset_demo():
    # Local classroom demo utility. Keep the server bound to localhost unless you add authentication.
    with connect() as db:
        db.execute('DELETE FROM attempts')
    for photo in PHOTOS.glob('*.jpg'):
        try: photo.unlink()
        except OSError: pass
    return jsonify({'ok': True})


init_db()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
