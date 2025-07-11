import streamlit as st
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import tempfile
import os
import math

def simple_silence_detection(audio, min_silence_len=500, silence_thresh=-40, 
                            keep_silence=100, seek_step=1):
    """
    Simple but effective silence detection using pydub
    """
    # Use pydub's built-in silence detection
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
        seek_step=seek_step
    )
    
    return chunks

def adaptive_threshold_simple(audio):
    """
    Simple adaptive threshold based on audio statistics
    """
    # Get audio statistics
    samples = audio.get_array_of_samples()
    
    # Calculate RMS
    rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
    
    # Convert to dB
    if rms > 0:
        rms_db = 20 * math.log10(rms / (2**15))  # Assuming 16-bit audio
    else:
        rms_db = -60
    
    # Use a percentage of the RMS as threshold
    adaptive_threshold = rms_db - 20  # 20dB below RMS
    
    # Clamp to reasonable range
    return max(-60, min(-20, adaptive_threshold))

def main():
    st.title("🎵 Audio Silence Trimmer (Simple Version)")
    st.markdown("**Easy-to-use audio trimming with natural gap preservation**")
    
    # File upload
    audio_file = st.file_uploader("Upload audio or video file", type=["wav", "mp3", "mp4", "ogg", "m4a"])
    
    # Settings
    st.sidebar.header("🔧 Settings")
    
    # Detection method
    detection_method = st.sidebar.selectbox(
        "Silence Detection Method",
        ["Adaptive (Recommended)", "Manual Threshold"],
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
    output_format = st.sidebar.selectbox("Output Format", ["mp3", "wav"])
    bitrate = st.sidebar.selectbox("MP3 Bitrate", ["128k", "192k", "256k", "320k"]) if output_format == "mp3" else None
    
    # Processing options
    st.sidebar.header("⚙️ Processing Options")
    normalize_audio = st.sidebar.checkbox("Normalize audio levels", value=True,
                                         help="Ensures consistent volume levels")
    
    if audio_file and st.button("🚀 Process Audio", type="primary"):
        with st.spinner("Analyzing and trimming audio..."):
            # Create temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_input:
                tmp_input.write(audio_file.read())
                input_path = tmp_input.name
                
            output_path = os.path.join(tempfile.gettempdir(), f"trimmed_audio.{output_format}")
            
            # Load audio
            if input_path.endswith(".mp4"):
                audio = AudioSegment.from_file(input_path, format="mp4")
            else:
                audio = AudioSegment.from_file(input_path)
            
            # Show original audio info
            original_duration = len(audio) / 1000
            st.info(f"📁 Original audio: {original_duration:.1f} seconds")
            
            # Adaptive threshold detection
            if detection_method == "Adaptive (Recommended)":
                adaptive_thresh = adaptive_threshold_simple(audio)
                threshold = adaptive_thresh
                st.info(f"📊 Adaptive threshold detected: {threshold:.1f} dB")
            
            # Silence detection
            chunks = simple_silence_detection(
                audio, min_silence, threshold, keep_silence, seek_step
            )
            
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
                st.info(f"⏱️ Original: {original_duration:.1f}s → Trimmed: {final_duration:.1f}s")
                st.info(f"💾 Time saved: {time_saved:.1f}s ({reduction_percent:.1f}% reduction)")
                st.info(f"🎵 Segments preserved: {len(chunks)}")
                
                # Audio player
                st.audio(output_path, format=f"audio/{output_format}")
                
                # Download button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download Trimmed Audio ({output_format.upper()})",
                        data=f,
                        file_name=f"trimmed_audio.{output_format}",
                        mime=f"audio/{output_format}"
                    )
                
                # Show processing info
                st.subheader("📊 Processing Information")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Original Duration", f"{original_duration:.1f}s")
                
                with col2:
                    st.metric("Final Duration", f"{final_duration:.1f}s")
                
                with col3:
                    st.metric("Time Saved", f"{time_saved:.1f}s")
                
                # Show segments info
                st.subheader("🎵 Audio Segments")
                st.write(f"**{len(chunks)} segments** were preserved after trimming")
                
                if len(chunks) > 0:
                    segment_durations = [len(chunk) / 1000 for chunk in chunks]
                    avg_duration = sum(segment_durations) / len(segment_durations)
                    st.write(f"**Average segment length:** {avg_duration:.1f} seconds")
                    st.write(f"**Longest segment:** {max(segment_durations):.1f} seconds")
                    st.write(f"**Shortest segment:** {min(segment_durations):.1f} seconds")
                
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