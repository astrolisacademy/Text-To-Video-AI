from openai import OpenAI
import os
import json
import re
from datetime import datetime
from utility.utils import log_response,LOG_TYPE_GPT

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
    model = "llama3-70b-8192"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    model = "gpt-4o"
    OPENAI_API_KEY = os.environ.get('OPENAI_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

log_directory = ".logs/gpt_logs"

prompt = """# Instructions

Given the following video script and timed captions, extract three visually concrete and specific keywords for each time segment that can be used to search for background videos. The keywords should be short and capture the main essence of the sentence. They can be synonyms or related terms. If a caption is vague or general, consider the next timed caption for more context. If a keyword is a single word, try to return a two-word keyword that is visually concrete. If a time frame contains two or more important pieces of information, divide it into shorter time frames with one keyword each. Ensure that the time periods are strictly consecutive and cover the entire length of the video. Each keyword should cover between 2-4 seconds. The output should be in JSON format, like this: [[[t1, t2], ["keyword1", "keyword2", "keyword3"]], [[t2, t3], ["keyword4", "keyword5", "keyword6"]], ...]. Please handle all edge cases, such as overlapping time segments, vague or general captions, and single-word keywords.

For example, if the caption is 'The cheetah is the fastest land animal, capable of running at speeds up to 75 mph', the keywords should include 'cheetah running', 'fastest animal', and '75 mph'. Similarly, for 'The Great Wall of China is one of the most iconic landmarks in the world', the keywords should be 'Great Wall of China', 'iconic landmark', and 'China landmark'.

Important Guidelines:

Use only English in your text queries.
Each search string must depict something visual.
The depictions have to be extremely visually concrete, like rainy street, or cat sleeping.
'emotional moment' <= BAD, because it doesn't depict something visually.
'crying child' <= GOOD, because it depicts something visual.
The list must always contain the most relevant and appropriate query searches.
['Car', 'Car driving', 'Car racing', 'Car parked'] <= BAD, because it's 4 strings.
['Fast car'] <= GOOD, because it's 1 string.
['Un chien', 'une voiture rapide', 'une maison rouge'] <= BAD, because the text query is NOT in English.

Note: Your response should be the response only and no extra text or data.
  """

def fix_json(json_str):
    # Remove markdown JSON fences if any
    json_str = re.sub(r"```json|```", "", json_str)

    # Replace fancy quotes with straight quotes
    replacements = {
        "“": "\"",
        "”": "\"",
        "‘": "'",
        "’": "'",
        "«": "\"",
        "»": "\"",
    }
    for k, v in replacements.items():
        json_str = json_str.replace(k, v)

    # Fix unescaped quotes inside strings:
    # Replace occurrences of "word"some"word" to "word\"some\"word"
    # This is tricky but try a regex to escape quotes inside array elements:
    def escape_inner_quotes(match):
        inner = match.group(0)
        inner_escaped = inner.replace('"', '\\"')
        return inner_escaped

    # A simpler approach: escape quotes between brackets ["..."]
    # but careful not to double escape

    # Remove trailing commas before closing brackets/braces (common JSON error)
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

    return json_str

def getVideoSearchQueriesTimed(script, captions_timed, custom_keywords=None):
    end = captions_timed[-1][0][1]

    # If custom keywords are provided, use them instead of calling AI
    if custom_keywords:
        # Parse the comma-separated string into a list of keywords
        if isinstance(custom_keywords, str):
            keyword_list = [kw.strip() for kw in custom_keywords.split(',')][:3]
        else:
            keyword_list = custom_keywords[:3]

        # Ensure we have exactly 3 keywords
        while len(keyword_list) < 3:
            keyword_list.append(keyword_list[0])

        # Create time segments using the captions_timed
        result = []
        for caption in captions_timed:
            time_segment = caption[0]
            result.append([time_segment, keyword_list])

        return result

    # Original AI-based generation logic
    try:
        out = [[[0,0],""]]
        while out[-1][0][1] != end:
            content = call_OpenAI(script,captions_timed).replace("'",'"')
            try:
                out = json.loads(content)
            except Exception as e:
                print("content: \n", content, "\n\n")
                print(e)
                content = fix_json(content.replace("```json", "").replace("```", ""))
                out = json.loads(content)
        return out
    except Exception as e:
        print("error in response",e)

    return None

def call_OpenAI(script,captions_timed):
    user_content = """Script: {}
Timed Captions:{}
""".format(script,"".join(map(str,captions_timed)))
    print("Content", user_content)
    
    response = client.chat.completions.create(
        model= model,
        temperature=1,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )
    
    text = response.choices[0].message.content.strip()
    text = re.sub('\s+', ' ', text)
    print("Text", text)
    log_response(LOG_TYPE_GPT,script,text)
    return text

def merge_empty_intervals(segments):
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]
        if url is None:
            # Find consecutive None intervals
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            # Merge consecutive None intervals with the previous valid URL
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged
