from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename
from videoTrans import VideoTranscriber  # Import the VideoTranscriber class

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)
        
        # Process video
        transcriber = VideoTranscriber(model_path='base', video_path=video_path)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename.rsplit(".", 1)[0]}.mp3')
        transcriber.extract_audio(output_audio_path=audio_path)
        transcriber.transcribe_video()
        output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], f'output_{filename}')
        transcriber.create_video(output_video_path)
        transcriber.clearframs()
        
        return redirect(url_for('download_file', filename=f'output_{filename}'))
    else:
        return 'Invalid file format. Please upload a video file.'

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
