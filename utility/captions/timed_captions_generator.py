import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re

def generate_timed_captions(audio_filename, model_size="base"):
    WHISPER_MODEL = load_model(model_size)
    gen = transcribe_timestamped(WHISPER_MODEL, audio_filename, verbose=False, fp16=False)
    return getCaptionsWithTime(gen)

def getTimestampMapping(whisper_analysis):
    index = 0
    locationToTimestamp = {}
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            newIndex = index + len(word['text'])+1
            locationToTimestamp[(index, newIndex)] = word['end']
            index = newIndex
    return locationToTimestamp

def interpolateTimeFromDict(word_position, d):
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def split_into_lines(sentence, max_chars_per_line=40):
    words = sentence.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_chars_per_line:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word) + 1

    if current_line:
        lines.append(' '.join(current_line))

    # Combine into maximum two lines
    if len(lines) > 2:
        # If more than 2 lines, combine the remaining lines into the second line
        lines = [lines[0], ' '.join(lines[1:])]

    return '\n'.join(lines)

def getCaptionsWithTime(whisper_analysis, max_chars_per_line=40):
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    position = 0
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis['text']

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    for sentence in sentences:
        words = sentence.split()
        sentence_text = ' '.join(words)

        # Format the sentence into proper subtitle lines
        formatted_text = split_into_lines(sentence_text, max_chars_per_line)

        # Update position for timestamp calculation
        position += len(sentence_text) + 1
        end_time = interpolateTimeFromDict(position, wordLocationToTime)

        if end_time and formatted_text:
            CaptionsPairs.append(((start_time, end_time), formatted_text))
            start_time = end_time

    return CaptionsPairs