import streamlit as st
import os
import glob

# Handling MoviePy version differences
try:
    from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
except ImportError:
    from moviepy import ImageClip, concatenate_videoclips, AudioFileClip

import yt_dlp

# ---------------------------------------------------
# 1. INITIALIZE SESSION STATE
# ---------------------------------------------------

if 'audio_path' not in st.session_state:
    st.session_state['audio_path'] = None

if 'yt_error' not in st.session_state:
    st.session_state['yt_error'] = None

# ---------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------

def cleanup_temp_files():
    """Delete temporary files."""
    
    files = glob.glob("temp_*") + ["output_video.mp4"]

    for f in files:
        try:
            os.remove(f)
        except:
            pass

    st.session_state['audio_path'] = None
    st.session_state['yt_error'] = None


def download_youtube_audio(url):
    """Download YouTube audio using yt-dlp."""

    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',

        'http_headers': {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'Referer': 'https://www.google.com/',
        },

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(audio_opts) as ydl:
        ydl.download([url])

    return "temp_audio.mp3"


def handle_youtube_download(url):

    try:
        st.session_state['yt_error'] = None

        audio_path = download_youtube_audio(url)

        if audio_path:
            st.session_state['audio_path'] = audio_path

    except Exception as e:
        st.session_state['yt_error'] = str(e)


def create_video(image_files, duplicate_count, fps, audio_path):

    clips = []

    duration_per_image = duplicate_count / fps

    target_resolution = (1280, 720)

    # ---------------------------------------------
    # Convert Uploaded Images into Video Clips
    # ---------------------------------------------

    for idx, img_file in enumerate(image_files):

        temp_img_path = f"temp_img_{idx}.png"

        with open(temp_img_path, "wb") as f:
            f.write(img_file.getbuffer())

        clip = ImageClip(temp_img_path)

        # MoviePy compatibility
        try:
            clip = clip.with_duration(duration_per_image)
        except:
            clip = clip.set_duration(duration_per_image)

        # Resize
        try:
            clip = clip.resize(target_resolution)
        except:
            clip = clip.resized(target_resolution)

        clips.append(clip)

    # ---------------------------------------------
    # Merge Video Clips
    # ---------------------------------------------

    final_video = concatenate_videoclips(clips, method="compose")

    try:
        final_video = final_video.with_fps(fps)
    except:
        final_video = final_video.set_fps(fps)

    # ---------------------------------------------
    # Add Audio
    # ---------------------------------------------

    audio_clip = AudioFileClip(audio_path)

    # Trim audio if longer than video
    if audio_clip.duration > final_video.duration:
        audio_clip = audio_clip.subclip(0, final_video.duration)

    try:
        final_clip = final_video.with_audio(audio_clip)
    except:
        final_clip = final_video.set_audio(audio_clip)

    # ---------------------------------------------
    # Export Video
    # ---------------------------------------------

    output_filename = "output_video.mp4"

    final_clip.write_videofile(
        output_filename,
        codec="libx264",
        audio_codec="aac"
    )

    return output_filename

# ---------------------------------------------------
# 3. STREAMLIT UI
# ---------------------------------------------------

st.set_page_config(
    page_title="PragyanAI Video Creator",
    layout="wide"
)

# ---------------------------------------------------
# Logo
# ---------------------------------------------------

if os.path.exists("PragyanAI_Transperent.png"):
    st.image("PragyanAI_Transperent.png", width=300)

# ---------------------------------------------------
# Title
# ---------------------------------------------------

st.title("🎬 PragyanAI - Multimedia Merger")

st.markdown(
    """
    Upload multiple images, add audio from file or YouTube,
    and create a professional slideshow video automatically.
    """
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.header("⚙ Video Settings")

    fps = st.slider(
        "Frames Per Second (FPS)",
        min_value=1,
        max_value=60,
        value=24
    )

    duplicates = st.number_input(
        "Frames Per Image",
        min_value=1,
        value=48
    )

    st.markdown("---")

    if st.button("🧹 Clear Cache & Temp Files"):

        cleanup_temp_files()

        st.success("Temporary files deleted!")

        st.rerun()

# ---------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------

col1, col2 = st.columns(2)

# ---------------------------------------------------
# IMAGE SECTION
# ---------------------------------------------------

with col1:

    st.subheader("🖼 Upload Images")

    uploaded_images = st.file_uploader(
        "Upload Image Sequence",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_images:
        st.success(f"{len(uploaded_images)} Images Uploaded")

# ---------------------------------------------------
# AUDIO SECTION
# ---------------------------------------------------

with col2:

    st.subheader("🎵 Audio Input")

    # Upload Audio
    uploaded_audio = st.file_uploader(
        "Upload Audio File",
        type=["mp3", "wav"]
    )

    # YouTube URL
    youtube_url = st.text_input(
        "Or Paste YouTube URL"
    )

    # Download Button
    if st.button("⬇ Download YouTube Audio"):

        if youtube_url:

            with st.spinner("Downloading audio from YouTube..."):

                handle_youtube_download(youtube_url)

            if st.session_state['yt_error']:
                st.error(st.session_state['yt_error'])

            else:
                st.success("YouTube audio downloaded!")

    # Save Uploaded Audio
    if uploaded_audio:

        temp_audio_path = "temp_uploaded_audio.mp3"

        with open(temp_audio_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())

        st.session_state['audio_path'] = temp_audio_path

        st.success("Audio uploaded successfully!")

# ---------------------------------------------------
# CREATE VIDEO BUTTON
# ---------------------------------------------------

st.markdown("---")

if st.button("🎥 Create Video"):

    if not uploaded_images:
        st.error("Please upload images.")

    elif not st.session_state['audio_path']:
        st.error("Please upload audio or download from YouTube.")

    else:

        with st.spinner("Creating video... Please wait ⏳"):

            output_video = create_video(
                uploaded_images,
                duplicates,
                fps,
                st.session_state['audio_path']
            )

        st.success("✅ Video Created Successfully!")

        # Show Video
        st.video(output_video)

        # Download Button
        with open(output_video, "rb") as file:

            st.download_button(
                label="⬇ Download Video",
                data=file,
                file_name="PragyanAI_Output.mp4",
                mime="video/mp4"
            )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")
st.caption("🚀 Built with Streamlit + MoviePy + yt-dlp")
