from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.captions.srt_generator import generate_srt
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
import argparse
import re

def sanitize_folder_name(name):
    """Convert topic to a valid folder name"""
    # Replace spaces with underscores and remove invalid characters
    sanitized = re.sub(r'[^\w\-_]', '_', name)
    # Convert to lowercase and remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized.lower())
    return sanitized.strip('_')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")
    parser.add_argument("--base-output-dir", type=str, default="output", help="Base output directory")

    args = parser.parse_args()

    # Create topic-specific output directory
    topic_folder_name = sanitize_folder_name(args.topic)
    output_dir = os.path.join(args.base_output_dir, topic_folder_name)
    os.makedirs(output_dir, exist_ok=True)

    SAMPLE_TOPIC = args.topic
    SAMPLE_FILE_NAME = os.path.join(output_dir, "audio_tts.wav")
    VIDEO_SERVER = "pexel"

    response = generate_script(SAMPLE_TOPIC)
    print("script: {}".format(response))

    # Save the script to a text file in the topic folder
    script_file = os.path.join(output_dir, "script.txt")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(response)

    asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    print(timed_captions)

    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    print(search_terms)

    background_video_urls = None
    if search_terms is not None:
        background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
        print(background_video_urls)
    else:
        print("No background video")

    background_video_urls = merge_empty_intervals(background_video_urls)

    if background_video_urls is not None:
        # Generate video with topic-specific output directory
        output_video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER, output_dir)
        if output_video:
            # Generate matching SRT file in the same topic folder
            output_srt = os.path.join(output_dir, os.path.splitext(os.path.basename(output_video))[0] + ".srt")
            generate_srt(timed_captions, output_srt)
            print(f"Generated video: {output_video}")
            print(f"Generated subtitles: {output_srt}")
            print(f"All files are in: {output_dir}")
        else:
            print("Failed to generate video")
    else:
        print("No video")