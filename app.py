with col2:
    st.subheader("2. Audio")

    audio_file = st.file_uploader(
        "Upload Audio File",
        type=["mp3", "wav"]
    )

    youtube_url = st.text_input("Or Enter YouTube URL")

    if st.button("Download YouTube Audio"):
        if youtube_url:
            handle_youtube_download(youtube_url)

    if audio_file:
        with open("temp_uploaded_audio.mp3", "wb") as f:
            f.write(audio_file.getbuffer())
        st.session_state['audio_path'] = "temp_uploaded_audio.mp3"

    if st.session_state['audio_path']:
        st.success("Audio Ready!")

if st.button("Create Video"):
    if uploaded_images and st.session_state['audio_path']:
        with st.spinner("Creating video..."):
            output_video = create_video(
                uploaded_images,
                duplicates,
                fps,
                st.session_state['audio_path']
            )

        st.success("Video Created Successfully!")

        st.video(output_video)

        with open(output_video, "rb") as file:
            st.download_button(
                "Download Video",
                file,
                file_name="final_video.mp4"
            )
    else:
        st.error("Please upload images and audio.")
