import os
from flask import Flask, request, Response
import requests

app = Flask(__name__)

# BotFather থেকে পাওয়া আপনার টেলিগ্রাম বটের টোকেন
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

@app.route('/')
def home():
    return "Telegram Streaming Server is Running!"

@app.route('/stream')
def stream_video():
    file_id = request.args.get('file_id')
    if not file_id:
        return "Missing file_id parameter", 400

    # ১. টেলিগ্রাম থেকে ফাইলের রিয়েল পাথ নেওয়া
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    res = requests.get(get_file_url).json()
    
    if not res.get("ok"):
        return "Invalid file_id or bot token", 400
        
    file_path = res["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # ২. ভিডিও ফরওয়ার্ড বা রিওয়াইন্ড করার জন্য Range Header ফরওয়ার্ড করা
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)