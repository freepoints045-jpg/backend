import os
from flask import Flask, request, Response
import requests

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8790126154:AAE7Sx6SS8qtJonKJSjZbpzcf0tXlICLi10")

@app.route('/')
def home():
    return "Vercel Telegram Streamer is Running!"

@app.route('/stream')
def stream_video():
    file_id = request.args.get('file_id')
    if not file_id:
        return "Missing file_id", 400

    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(get_file_url).json()
    
    if not res.get("ok"):
        return "Invalid file_id", 400
        
    file_path = res["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    range_header = request.headers.get('Range', None)
    headers = {}
    if range_header:
        headers['Range'] = range_header

    req = requests.get(download_url, headers=headers, stream=True)

    resp_headers = {
        'Content-Type': req.headers.get('Content-Type', 'video/mp4'),
        'Accept-Ranges': 'bytes',
    }
    
    if 'Content-Range' in req.headers:
        resp_headers['Content-Range'] = req.headers['Content-Range']
    if 'Content-Length' in req.headers:
        resp_headers['Content-Length'] = req.headers['Content-Length']

    return Response(req.iter_content(chunk_size=1024*1024), status=req.status_code, headers=resp_headers)
