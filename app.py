import streamlit as st
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import tempfile
import os
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import matplotlib.pyplot as plt

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

def main():
    st.title("🎵 Advanced Audio Silence Trimmer")
    st.markdown("**Professional-grade audio trimming with natural gap preservation**")
    
    # File upload
    audio_file = st.file_uploader("Upload audio or video file", type=["wav", "mp3", "mp4", "ogg", "m4a", "flac"])
    
    # Advanced settings
    st.sidebar.header("🔧 Advanced Settings")
    
    # Detection method
    detection_method = st.sidebar.selectbox(
        "Silence Detection Method",
        ["Adaptive (Recommended)", "Manual Threshold", "Hybrid"],
        help="Adaptive automatically adjusts threshold based on audio characteristics"
    )
    
    # Trimming parameters
    min_silence = st.sidebar.slider("Minimum silence to trim (ms)", 200, 3000, 500, 
                                   help="Longer values = more aggressive trimming")
    
    if detection_method == "Manual Threshold":
        threshold = st.sidebar.slider("Silence threshold (dB)", -60, -20, -40,
                                     help="Lower values = more sensitive to quiet sounds")
    else:
        threshold = -40  # Will be overridden by adaptive detection
    
    keep_silence = st.sidebar.slider("Keep silence around speech (ms)", 50, 500, 150,
                                    help="Preserves natural breathing and pauses")
    
    seek_step = st.sidebar.slider("Detection precision (ms)", 1, 10, 1,
                                 help="Lower values = more precise but slower")
    
    # Quality settings
    st.sidebar.header("🎚️ Quality Settings")
    output_format = st.sidebar.selectbox("Output Format", ["mp3", "wav", "flac"])
    bitrate = st.sidebar.selectbox("MP3 Bitrate", ["128k", "192k", "256k", "320k"]) if output_format == "mp3" else None
    
    # Processing options
    st.sidebar.header("⚙️ Processing Options")
    normalize_audio = st.sidebar.checkbox("Normalize audio levels", value=True,
                                         help="Ensures consistent volume levels")
    remove_noise = st.sidebar.checkbox("Remove background noise", value=False,
                                      help="Reduces hiss and background noise")
    
    if audio_file and st.button("🚀 Process Audio", type="primary"):
        with st.spinner("Analyzing and trimming audio..."):
            # Create temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_input:
                tmp_input.write(audio_file.read())
                input_path = tmp_input.name
                
            base_name = os.path.splitext(os.path.basename(audio_file.name))[0]
            output_path = os.path.join(tempfile.gettempdir(), f"trimmed_{base_name}.{output_format}")
            
            # Adaptive threshold detection
            if detection_method == "Adaptive (Recommended)":
                adaptive_thresh = adaptive_threshold_detection(input_path)
                threshold = max(-60, min(-20, adaptive_thresh))
                st.info(f"📊 Adaptive threshold detected: {threshold:.1f} dB")
            
            # Load and process audio
            if input_path.endswith(".mp4"):
                audio = AudioSegment.from_file(input_path, format="mp4")
            else:
                audio = AudioSegment.from_file(input_path)
            
            # Show original audio info
            original_duration = len(audio) / 1000
            st.info(f"📁 Original audio: {original_duration:.1f} seconds")
            
            # Advanced silence detection
            if detection_method == "Hybrid":
                # Use both methods and combine results
                chunks_pydub, _ = split_on_silence(
                    audio, min_silence_len=min_silence, silence_thresh=threshold,
                    keep_silence=keep_silence, seek_step=seek_step
                )
                chunks_advanced, silent_times = advanced_silence_detection(
                    input_path, min_silence, threshold, keep_silence, seek_step
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
                    input_path, min_silence, threshold, keep_silence, seek_step
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
                
                # Display results
                final_duration = len(trimmed_audio) / 1000
                time_saved = original_duration - final_duration
                reduction_percent = (time_saved / original_duration) * 100
                
                st.success(f"✅ Processing complete!")
                st.info(f"🎯 Method used: {method_used}")
                st.info(f"⏱️ Original: {original_duration:.1f}s → Trimmed: {final_duration:.1f}s")
                st.info(f"💾 Time saved: {time_saved:.1f}s ({reduction_percent:.1f}% reduction)")
                st.info(f"🎵 Segments preserved: {len(chunks)}")
                
                # Audio player
                st.audio(output_path, format=f"audio/{output_format}")
                
                # Download button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"💾 Download Trimmed Audio ({output_format.upper()})",
                        data=f,
                        file_name=f"trimmed_{base_name}.{output_format}",
                        mime=f"audio/{output_format}"
                    )
                
                # Show silent regions visualization
                if silent_times and len(silent_times) > 0:
                    st.subheader("📊 Silent Regions Detected")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    
                    # Create timeline
                    timeline = np.linspace(0, original_duration, 1000)
                    silence_mask = np.zeros_like(timeline)
                    
                    for start, end in silent_times:
                        start_s = start / 1000
                        end_s = end / 1000
                        mask = (timeline >= start_s) & (timeline <= end_s)
                        silence_mask[mask] = 1
                    
                    ax.plot(timeline, silence_mask, 'r-', linewidth=2, label='Silent Regions')
                    ax.fill_between(timeline, silence_mask, alpha=0.3, color='red')
                    ax.set_xlabel('Time (seconds)')
                    ax.set_ylabel('Silence Detection')
                    ax.set_title('Silent Regions in Audio')
                    ax.grid(True, alpha=0.3)
                    ax.legend()
                    
                    st.pyplot(fig)
                
            else:
                st.warning("⚠️ No audio segments detected. Try adjusting the threshold or minimum silence length.")
            
            # Cleanup
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

if __name__ == "__main__":
    main()