# Cheating Detection System

This is a web-based application designed to detect cheating behavior in videos. The system processes uploaded videos, extracts frames, and allows for both automatic and manual labeling of frames to identify potential cheating behavior.

## System Components

### 1. Web Interface (`templates/index.html`)
- Provides a user-friendly interface for video upload
- Displays frames for manual review and labeling
- Shows analysis results including:
  - Total frames analyzed
  - Number of frames with cheating detected
  - Percentage of cheating frames
  - Overall conclusion

### 2. Main Application (`app.py`)
- Flask web server handling all HTTP requests
- Features:
  - Video upload handling with security measures
  - Frame extraction coordination
  - Database interactions for storing annotations
  - Analysis endpoints for results
- Routes:
  - `/`: Main page with upload interface
  - `/upload`: Handles video file uploads
  - `/api/save_label`: Saves frame annotations
  - `/api/analysis/<video_name>`: Provides analysis results

### 3. Frame Extraction (`extract_frames.py`)
- Processes uploaded videos using OpenCV
- Extracts one frame per second
- Saves frames as JPEG images with naming format: `videoname_frameX_tY.jpg`
  - X: Frame number
  - Y: Timestamp in seconds
- Output saved to `static/frames/` directory

### 4. Automatic Labeling (`auto_label_frames.py`)
- Implements automatic detection of potential cheating behavior
- Generates initial labels for frames
- Saves predictions to `predicted_labels.json`

### 5. Database Management (`database.py`)
- Handles PostgreSQL database connections
- Stores frame annotations including:
  - Video name
  - Frame name
  - Frame number
  - Timestamp
  - Label (Cheating/Not Cheating)

## Directory Structure
```
├── app.py                 # Main Flask application
├── auto_label_frames.py   # Automatic frame labeling
├── database.py           # Database management
├── extract_frames.py     # Video frame extraction
├── requirements.txt      # Python dependencies
├── input_videos/         # Uploaded video storage
├── static/
│   └── frames/          # Extracted frame storage
└── templates/
    └── index.html       # Web interface
```

## How It Works

1. **Video Upload**
   - User uploads a video through the web interface
   - System generates a unique filename and saves to `input_videos/`
   - Supported formats: MP4, AVI, MOV

2. **Frame Extraction**
   - System processes the video using OpenCV
   - Extracts one frame per second
   - Saves frames to `static/frames/` directory

3. **Automatic Labeling**
   - System automatically analyzes extracted frames
   - Generates initial predictions for each frame
   - Saves predictions to JSON file

4. **Manual Review**
   - User reviews each frame in the web interface
   - Can mark frames as "Cheating" or "Not Cheating"
   - Labels are stored in the database

5. **Analysis**
   - After all frames are labeled, system generates analysis
   - Considers video as "Cheating" if >30% of frames show cheating
   - Provides detailed statistics and overall conclusion

## Requirements

- Python 3.x
- OpenCV (cv2)
- Flask
- PostgreSQL
- Additional requirements in `requirements.txt`

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the PostgreSQL database using the schema in `database.py`

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Security Features

- Secure filename handling for uploads
- File type validation
- Maximum file size limit (16MB)
- Database query parameterization

## Development

To extend or modify the system:
1. Frame extraction settings can be adjusted in `extract_frames.py`
2. Automatic labeling logic can be modified in `auto_label_frames.py`
3. Analysis thresholds can be changed in `app.py`

## Note

This system is designed for educational purposes and should be used responsibly. The accuracy of cheating detection depends on various factors including video quality, camera angle, and the specific behaviors being monitored.
