def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt(timed_captions, output_file):
    """Generate SRT file from timed captions"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, ((start_time, end_time), text) in enumerate(timed_captions, 1):
            # Write subtitle number
            f.write(f"{i}\n")

            # Write timestamp
            f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")

            # Write text
            f.write(f"{text}\n")

            # Write blank line
            f.write("\n")