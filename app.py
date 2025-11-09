from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from database import init_db
from extract_frames import extract_frames
from auto_label_frames import auto_label_frames
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'input_videos'

# Initialize database
conn = init_db()
cursor = conn.cursor()

# Ensure upload and frames directories exist
os.makedirs('input_videos', exist_ok=True)
os.makedirs('static/frames', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

# Load predicted labels (auto-labeled)
if os.path.exists("predicted_labels.json"):
    with open("predicted_labels.json") as f:
        prelabels = {item["frame_name"]: item["predicted_label"] for item in json.load(f)}
else:
    prelabels = {}

@app.route('/')
def index():
    return render_template('index.html', frames=[], labels=[])

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'status': 'error', 'message': 'No video file uploaded'})
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No video file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': f'Invalid file type. Allowed types are: mp4, avi, mov'})
    
    try:
        # Clear existing frames
        for f in os.listdir('static/frames'):
            if f.endswith('.jpg'):
                os.remove(os.path.join('static/frames', f))
        
        # Generate unique filename
        unique_filename = f"{str(uuid.uuid4())}_{secure_filename(file.filename)}"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(video_path)
        
        # Extract frames
        try:
            extract_frames(video_path, 'static/frames')
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error extracting frames: {str(e)}'})
        
        # Auto label frames
        try:
            auto_label_frames('static/frames')
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error auto-labeling frames: {str(e)}'})
        
        # Load predicted labels
        try:
            if os.path.exists("predicted_labels.json"):
                with open("predicted_labels.json") as f:
                    prelabels = {item["frame_name"]: item["predicted_label"] for item in json.load(f)}
            else:
                prelabels = {}
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error loading predictions: {str(e)}'})
        
        # Get frames and their labels
        frames = sorted(os.listdir('static/frames'))
        if not frames:
            return jsonify({'status': 'error', 'message': 'No frames were extracted from the video'})
            
        labels = [prelabels.get(f, "Not Labeled") for f in frames]
        
        return jsonify({
            'status': 'success',
            'frames': frames,
            'labels': labels
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Upload error: {str(e)}'})

@app.route('/api/save_label', methods=['POST'])
def save_label():
    data = request.json
    video_name = data['video_name']
    frame_name = data['frame_name']
    frame_number = data['frame_number']
    timestamp_sec = data['timestamp_sec']
    label = data['label']

    cursor.execute("""
        INSERT INTO annotations (video_name, frame_name, frame_number, timestamp_sec, label)
        VALUES (%s, %s, %s, %s, %s)
    """, (video_name, frame_name, frame_number, timestamp_sec, label))
    conn.commit()

    return jsonify({'status': 'success'})

@app.route('/api/annotations', methods=['GET'])
def get_all():
    cursor.execute("SELECT * FROM annotations")
    rows = cursor.fetchall()
    return jsonify(rows)

@app.route('/api/annotation/<frame_name>', methods=['GET'])
def get_annotation(frame_name):
    cursor.execute("SELECT * FROM annotations WHERE frame_name = %s", (frame_name,))
    row = cursor.fetchone()
    return jsonify(row if row else {})

@app.route('/api/analysis/<video_name>', methods=['GET'])
def get_analysis(video_name):
    # Get all annotations for the video
    cursor.execute("""
        SELECT label, COUNT(*) as count 
        FROM annotations 
        WHERE video_name = %s 
        GROUP BY label
    """, (video_name,))
    
    results = cursor.fetchall()
    
    # Calculate statistics
    total_frames = sum(r[1] for r in results)
    cheating_frames = sum(r[1] for r in results if r[0] == 'Cheating')
    cheating_percentage = round((cheating_frames / total_frames * 100) if total_frames > 0 else 0, 2)
    
    # Determine overall conclusion
    # If more than 30% of frames show cheating, consider it as cheating detected
    overall_conclusion = "Cheating Detected" if cheating_percentage > 30 else "No Cheating Detected"
    
    return jsonify({
        'total_frames': total_frames,
        'cheating_frames': cheating_frames,
        'cheating_percentage': cheating_percentage,
        'overall_conclusion': overall_conclusion
    })

if __name__ == '__main__':
    app.run(debug=True)
