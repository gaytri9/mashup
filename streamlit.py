# -*- coding: utf-8 -*-
"""streamlit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XH_4zt0wtEyiaITBrDfBlJobJDlu4w2u
"""

import streamlit as st
import os
pip install --upgrade pip
pip install pytube
pip install moviepy
from moviepy.editor import *
from pytube import YouTube
pip install youtube-search-python
from youtubesearchpython import VideosSearch
from email.message import EmailMessage
import pytube


OUTPUT_PATH = "static/mashup/"
GMAIL_USERNAME = "your.gmail@gmail.com"
GMAIL_PASSWORD = "yourpassword"
OUTPUT_PATH = "static/mashup/"

def fetch_video_clips(artist_name, num_clips):
    """
    Retrieve video clips from YouTube based on the artist's name.
    """
    prefix = "https://www.youtube.com/watch?v="
    search_results = VideosSearch(artist_name, limit=num_clips).result()["result"]
    video_urls = [prefix + result["id"] for result in search_results]
    return video_urls

def download_video_clip(video_url, save_path=OUTPUT_PATH):
    """
    Download a video clip from YouTube.
    """
    save_dir = os.path.join(save_path, "clips")
    yt = YouTube(video_url)
    video = yt.streams.first()
    video_title = video.default_filename.replace(" ", "_")
    video.download(save_dir, video_title)
    return video_title

def convert_to_audio(video_title, save_path=OUTPUT_PATH):
    """
    Convert a video clip to an audio file.
    """
    audio_save_path = save_path
    video_path = os.path.join(save_path, "clips", video_title)
    audio_path = os.path.join(audio_save_path, f"{video_title.split('.')[0]}.mp3")
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)
    audio_clip.close()
    video_clip.close()
    return audio_path

def trim_audio_file(audio_path, duration):
    """
    Trim an audio file to the specified duration.
    """
    audio_clip = AudioFileClip(audio_path)
    audio_clip = audio_clip.subclip(0, duration)
    trimmed_audio_path = audio_path[:-4] + "_trimmed.mp3"
    audio_clip.write_audiofile(trimmed_audio_path)
    audio_clip.close()

def download_and_process_video_clip(video_url, save_path, duration):
    """
    Download a video clip, convert it to audio, and trim it.
    """
    clip_title = download_video_clip(video_url, save_path)
    audio_title = convert_to_audio(clip_title, save_path)
    trim_audio_file(audio_title, duration)

def merge_audio_files(artist_name, save_path=OUTPUT_PATH, output_filename="mashup.mp3"):
    """
    Merge trimmed audio files into a single audio file.
    """
    final_audio_path = os.path.join(save_path, output_filename)
    audio_files = [os.path.join(save_path, audio) for audio in os.listdir(save_path) if audio.endswith("trimmed.mp3")]
    audio_clips = [AudioFileClip(audio) for audio in audio_files]
    final_clip = concatenate_audioclips(audio_clips)
    final_clip.write_audiofile(final_audio_path)
    final_clip.close()
    return final_audio_path

def send_email(attachment_path, attachment_filename):
    """
    Send an email with the mashup file attached.
    """
    msg = EmailMessage()
    msg['Subject'] = f"Mashup: {attachment_filename}"
    msg['From'] = GMAIL_USERNAME
    msg['To'] = GMAIL_USERNAME  # Change this to the recipient's email address

    # Body of the email
    msg.set_content("Please find the mashup attached.")

    # Attach the mashup file
    with open(attachment_path, 'rb') as file:
        file_data = file.read()
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=attachment_filename)

    # Connect to Gmail SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        smtp.send_message(msg)

def create_mashup(artist_name, num_clips, duration, output_filename,send_gmail):
    """
    Create a mashup by fetching, processing, and merging video clips.
    """
    save_path = os.path.join(OUTPUT_PATH, artist_name)
    video_urls = fetch_video_clips(artist_name, num_clips)

    for url in video_urls:
        download_and_process_video_clip(url, save_path, duration)

    mashup_path = merge_audio_files(artist_name, save_path, output_filename)

    if send_gmail:
        send_email(mashup_path, output_filename)

    return mashup_path

def main():
    """
    Main function for the Streamlit application.
    """
    st.title("YouTube Mashup Creator")

    artist_name = st.text_input("Enter Artist Name:")
    num_clips = st.number_input("Number of Clips:", min_value=1, step=1)
    duration = st.number_input("Duration (seconds):", min_value=1, step=1)
    output_filename = st.text_input("Output Filename:")

    send_gmail = st.checkbox("Send via Gmail")

    if not output_filename.endswith("trimmed.mp3"):
        output_filename += ".mp3"

    if st.button("Create Mashup"):
        mashup_path = create_mashup(artist_name, num_clips, duration, output_filename, send_gmail)
        st.success("Mashup created successfully!")
        st.download_button(label="Download Mashup", data=open(mashup_path, 'rb'), file_name=output_filename)

if __name__ == "__main__":
    main()
