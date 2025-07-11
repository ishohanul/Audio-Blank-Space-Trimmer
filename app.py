from flask import Flask, request, jsonify, send_file, render_template_string
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import tempfile
import os
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import matplotlib.pyplot as plt
import io
import base64
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 Advanced Audio Silence Trimmer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .upload-section {
            border: 2px dashed #ddd;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            transition: border-color 0.3s;
        }
        .upload-section:hover {
            border-color: #667eea;
        }
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .setting-group {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .setting-group h3 {
            margin-top: 0;
            color: #333;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        input[type="file"], select, input[type="range"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        input[type="range"] {
            margin-bottom: 5px;
        }
        .range-value {
            text-align: center;
            font-weight: bold;
            color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #e8f5e8;
            border-radius: 10px;
            display: none;
        }
        .error {
            background: #ffe6e6;
            color: #d63031;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .audio-player {
            margin-top: 20px;
        }
        .download-btn {
            background: #27ae60;
            margin-top: 10px;
        }
        .download-btn:hover {
            background: #229954;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Advanced Audio Silence Trimmer</h1>
        <p class="subtitle">Professional-grade audio trimming with natural gap preservation</p>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-section">
                <input type="file" id="audioFile" name="audio_file" accept=".wav,.mp3,.mp4,.ogg,.m4a,.flac" required>
                <p>Supported formats: WAV, MP3, OGG, M4A, FLAC, MP4</p>
            </div>
            
            <div class="settings-grid">
                <div class="setting-group">
                    <h3>🔧 Detection Settings</h3>
                    <label for="detection_method">Silence Detection Method:</label>
                    <select id="detection_method" name="detection_method">
                        <option value="adaptive">Adaptive (Recommended)</option>
                        <option value="manual">Manual Threshold</option>
                        <option value="hybrid">Hybrid</option>
                    </select>
                    
                    <label for="min_silence">Minimum silence to trim (ms): <span id="min_silence_value">500</span></label>
                    <input type="range" id="min_silence" name="min_silence" min="200" max="3000" value="500">
                    
                    <label for="threshold">Silence threshold (dB): <span id="threshold_value">-40</span></label>
                    <input type="range" id="threshold" name="threshold" min="-60" max="-20" value="-40">
                    
                    <label for="keep_silence">Keep silence around speech (ms): <span id="keep_silence_value">150</span></label>
                    <input type="range" id="keep_silence" name="keep_silence" min="50" max="500" value="150">
                </div>
                
                <div class="setting-group">
                    <h3>🎚️ Quality Settings</h3>
                    <label for="output_format">Output Format:</label>
                    <select id="output_format" name="output_format">
                        <option value="mp3">MP3</option>
                        <option value="wav">WAV</option>
                        <option value="flac">FLAC</option>
                    </select>
                    
                    <label for="bitrate">MP3 Bitrate:</label>
                    <select id="bitrate" name="bitrate">
                        <option value="128k">128k</option>
                        <option value="192k">192k</option>
                        <option value="256k">256k</option>
                        <option value="320k">320k</option>
                    </select>
                    
                    <label>
                        <input type="checkbox" id="normalize_audio" name="normalize_audio" checked>
                        Normalize audio levels
                    </label>
                    
                    <label>
                        <input type="checkbox" id="remove_noise" name="remove_noise">
                        Remove background noise
                    </label>
                </div>
            </div>
            
            <button type="submit">🚀 Process Audio</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing and trimming audio...</p>
        </div>
        
        <div class="results" id="results"></div>
    </div>

    <script>
        // Update range value displays
        document.getElementById('min_silence').addEventListener('input', function() {
            document.getElementById('min_silence_value').textContent = this.value;
        });
        
        document.getElementById('threshold').addEventListener('input', function() {
            document.getElementById('threshold_value').textContent = this.value;
        });
        
        document.getElementById('keep_silence').addEventListener('input', function() {
            document.getElementById('keep_silence_value').textContent = this.value;
        });
        
        // Handle form submission
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displayResults(result);
                } else {
                    const error = await response.text();
                    displayError(error);
                }
            } catch (error) {
                displayError('An error occurred while processing the audio.');
            } finally {
                loading.style.display = 'none';
            }
        });
        
        function displayResults(result) {
            const results = document.getElementById('results');
            results.innerHTML = `
                <h3>✅ Processing Complete!</h3>
                <p><strong>Method used:</strong> ${result.method_used}</p>
                <p><strong>Original duration:</strong> ${result.original_duration.toFixed(1)}s</p>
                <p><strong>Trimmed duration:</strong> ${result.final_duration.toFixed(1)}s</p>
                <p><strong>Time saved:</strong> ${result.time_saved.toFixed(1)}s (${result.reduction_percent.toFixed(1)}% reduction)</p>
                <p><strong>Segments preserved:</strong> ${result.segments_count}</p>
                
                <div class="audio-player">
                    <audio controls>
                        <source src="/download/${result.filename}" type="audio/${result.output_format}">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                
                <a href="/download/${result.filename}" class="download-btn" style="display: inline-block; text-decoration: none; color: white; padding: 10px 20px; border-radius: 5px;">
                    💾 Download Trimmed Audio
                </a>
            `;
            results.style.display = 'block';
        }
        
        function displayError(message) {
            const results = document.getElementById('results');
            results.innerHTML = `<div class="error">❌ ${message}</div>`;
            results.style.display = 'block';
        }
    </script>
</body>
</html>
"""

def advanced_silence_detection(audio_path, min_silence_len=500, silence_thresh=-40, 
                              keep_silence=100, seek_step=1, verbose=False):
    """
    Advanced silence detection using multiple algorithms for better accuracy
    """
    # Load audio with librosa for advanced analysis
    y, sr = librosa.load(audio_path, sr=None)
    
    # Method 1: Pydub silence detection (baseline)
    audio = AudioSegment.from_file(audio_path)
    chunks_pydub = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
        seek_step=seek_step
    )
    
    # Method 2: Librosa-based silence detection (more accurate)
    # Calculate RMS energy
    hop_length = int(sr * 0.01)  # 10ms hop
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    
    # Convert threshold to RMS scale
    silence_thresh_rms = 10**(silence_thresh/20)
    
    # Find silent regions
    silent_regions = rms < silence_thresh_rms
    
    # Convert to time segments
    silent_times = []
    start_silence = None
    
    for i, is_silent in enumerate(silent_regions):
        time = i * hop_length / sr * 1000  # Convert to milliseconds
        
        if is_silent and start_silence is None:
            start_silence = time
        elif not is_silent and start_silence is not None:
            if time - start_silence >= min_silence_len:
                silent_times.append((start_silence, time))
            start_silence = None
    
    # Handle case where audio ends with silence
    if start_silence is not None:
        end_time = len(y) / sr * 1000
        if end_time - start_silence >= min_silence_len:
            silent_times.append((start_silence, end_time))
    
    # Create non-silent segments
    non_silent_segments = []
    last_end = 0
    
    for start, end in silent_times:
        if start - last_end > 0:
            # Add non-silent segment
            segment_start = max(0, last_end - keep_silence)
            segment_end = min(len(audio), start + keep_silence)
            non_silent_segments.append(audio[segment_start:segment_end])
        last_end = end
    
    # Add final segment if there's audio after last silence
    if last_end < len(audio):
        segment_start = max(0, last_end - keep_silence)
        non_silent_segments.append(audio[segment_start:])
    
    return non_silent_segments, silent_times

def adaptive_threshold_detection(audio_path, window_size=1000):
    """
    Adaptive threshold detection that adjusts based on audio characteristics
    """
    y, sr = librosa.load(audio_path, sr=None)
    
    # Calculate adaptive threshold using percentile
    hop_length = int(sr * 0.01)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    
    # Use 10th percentile as adaptive threshold
    adaptive_threshold = np.percentile(rms, 10)
    
    # Convert to dB
    adaptive_threshold_db = 20 * np.log10(adaptive_threshold)
    
    return adaptive_threshold_db

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_audio():
    try:
        if 'audio_file' not in request.files:
            return 'No audio file uploaded', 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return 'No file selected', 400
        
        # Get form parameters
        detection_method = request.form.get('detection_method', 'adaptive')
        min_silence = int(request.form.get('min_silence', 500))
        threshold = int(request.form.get('threshold', -40))
        keep_silence = int(request.form.get('keep_silence', 150))
        output_format = request.form.get('output_format', 'mp3')
        bitrate = request.form.get('bitrate', '128k')
        normalize_audio = request.form.get('normalize_audio') == 'on'
        remove_noise = request.form.get('remove_noise') == 'on'
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp_input:
            file.save(tmp_input.name)
            input_path = tmp_input.name
        
        base_name = os.path.splitext(os.path.basename(file.filename))[0]
        output_filename = f"trimmed_{base_name}_{uuid.uuid4().hex[:8]}.{output_format}"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        
        # Adaptive threshold detection
        if detection_method == 'adaptive':
            adaptive_thresh = adaptive_threshold_detection(input_path)
            threshold = max(-60, min(-20, adaptive_thresh))
        
        # Load and process audio
        if input_path.endswith(".mp4"):
            audio = AudioSegment.from_file(input_path, format="mp4")
        else:
            audio = AudioSegment.from_file(input_path)
        
        # Show original audio info
        original_duration = len(audio) / 1000
        
        # Advanced silence detection
        if detection_method == 'hybrid':
            # Use both methods and combine results
            chunks_pydub, _ = split_on_silence(
                audio, min_silence_len=min_silence, silence_thresh=threshold,
                keep_silence=keep_silence, seek_step=1
            )
            chunks_advanced, silent_times = advanced_silence_detection(
                input_path, min_silence, threshold, keep_silence, 1
            )
            
            # Use the method that produces more segments (more aggressive trimming)
            if len(chunks_advanced) > len(chunks_pydub):
                chunks = chunks_advanced
                method_used = "Advanced Librosa"
            else:
                chunks = chunks_pydub
                method_used = "Pydub"
        else:
            chunks, silent_times = advanced_silence_detection(
                input_path, min_silence, threshold, keep_silence, 1
            )
            method_used = "Advanced Librosa"
        
        # Combine non-silent chunks
        if chunks:
            trimmed_audio = sum(chunks, AudioSegment.empty())
            
            # Audio post-processing
            if normalize_audio:
                trimmed_audio = trimmed_audio.normalize()
            
            # Export with quality settings
            export_params = {"format": output_format}
            if output_format == "mp3" and bitrate:
                export_params["bitrate"] = bitrate
            
            trimmed_audio.export(output_path, **export_params)
            
            # Calculate results
            final_duration = len(trimmed_audio) / 1000
            time_saved = original_duration - final_duration
            reduction_percent = (time_saved / original_duration) * 100
            
            # Clean up input file
            os.unlink(input_path)
            
            return jsonify({
                'success': True,
                'method_used': method_used,
                'original_duration': original_duration,
                'final_duration': final_duration,
                'time_saved': time_saved,
                'reduction_percent': reduction_percent,
                'segments_count': len(chunks),
                'filename': output_filename,
                'output_format': output_format
            })
        else:
            return 'No audio segments found after trimming', 400
            
    except Exception as e:
        return str(e), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return 'File not found', 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))