from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

def get_audio_formats(video_url):
    ydl_opts = {'listformats': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        formats = [f for f in info.get('formats', []) if f.get('vcodec') == 'none']
        return formats

@app.route('/')
def index():
    return render_template('index.html')  # Servir el archivo HTML desde la carpeta "templates"

@app.route('/formats', methods=['GET'])
def formats():
    video_url = request.args.get('videoUrl')
    formats = get_audio_formats(video_url)
    audio_formats = [
        {'format_id': f['format_id'], 'abr': f.get('abr', 'N/A'), 'acodec': f.get('acodec', 'N/A')}
        for f in formats
    ]
    return jsonify(audio_formats)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('videoUrl')
    format_id = request.args.get('formatId')

    ydl_opts = {
        'format': format_id,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

    return jsonify({'success': True, 'downloadUrl': f"/download/{os.path.basename(filename)}"})

@app.route('/download/<filename>')
def serve_download(filename):
    return send_file(f"downloads/{filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
