import argparse
import random
import re
import io
import os

from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
from num2words import num2words


def cloze_remover(cloze_string: str):
    return re.sub(r"\{\{\w*::(.*?)(::.*?)?\}\}", r"\1", cloze_string)


def make_filename(input_string, language_code, voice):
    # Replace spaces with underscores
    input_string = input_string.replace(" ", "_")
    # Remove any non-alphanumeric characters except underscores and dots
    input_string = "".join(c for c in input_string if c.isalnum() or c in "_.")
    if input_string[-1] == ".":
        input_string = input_string[:-1]
    # Add .mp3 extension if not already present
    if not input_string.endswith(".mp3"):
        input_string += ".mp3"

    # Return the modified string
    return language_code + "-" + voice + "_" + input_string


def replace_numbers(input_str):
    def callback(match):
        number = int(match.group())
        word = num2words(number, lang="de")
        return word

    return re.sub(r"\d+", callback, input_str)


def replace_money(input_str):
    """
    TODO: Write the Regex to match 8,60€ and things like that
    """

    def callback(match):
        number = int(match.group())
        word = num2words(number, lang="de")
        return word

    return NotImplementedError
    return re.sub(r"\d+", callback, input_str)


def tts_conversation(conversation: str):
    # First separate the conversation into a list
    conversation_list = conversation.split("@@")

    # Have two voices for the conversation
    voices = random.sample(["alloy", "echo", "fable", "onyx", "nova", "shimmer"], k=2)

    conversation = AudioSegment.empty()

    for i in range(len(conversation_list)):
        input_str = cloze_remover(conversation_list[i])
        input_str = replace_numbers(input_str)

        response = client.audio.speech.create(
            model="tts-1", voice=voices[i % 2], input=input_str
        )

        conversation += AudioSegment.from_mp3(io.BytesIO(response.content))
        if i != len(conversation_list):
            conversation += AudioSegment.silent(duration=600)

    conversation.export("conversation.mp3", format="mp3")


def tts(input_str):
    input_str = cloze_remover(input_str)

    # input_str = replace_money(input_str)

    input_str = replace_numbers(input_str)

    print(input_str)

    voice = random.choice(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

    filename_ai = make_filename(input_str, "DE", voice)
    output_folder_path = Path(__file__).parent / "output"
    speech_file_path = output_folder_path / filename_ai

    print(">\t", speech_file_path)

    response = client.audio.speech.create(model="tts-1", voice=voice, input=input_str)

    response.write_to_file(speech_file_path)


if __name__ == "__main__":
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    parser = argparse.ArgumentParser(description="Text to speech using OpenAI API")

    parser.add_argument("text", type=str, help="text that needs to be speech")
    parser.add_argument(
        "-c",
        "--conversation",
        action="store_true",
        help='treats text as conversation, separated by "@@"',
    )

    args = parser.parse_args()

    if args.conversation:
        tts_conversation(args.text)
    else:
        tts(args.text)
