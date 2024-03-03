import argparse
import random
import re
import io
import os

from dotenv import load_dotenv
from pathlib import Path
from pydub import AudioSegment
from num2words import num2words

from openai_tts import OpenAIClient
from azure_tts import AzureClient


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

    if language_code in voice:
        return voice + "_" + input_string
    else:
        return language_code + "-" + voice + "_" + input_string


def replace_numbers(input_str: str):
    def callback(match: re.Match):
        if "Uhr" in match.group():
            time_str: str = match.group().replace(" Uhr", "")
            hour_str, minute_str = time_str.split(".")
            formatted_time = (
                num2words(hour_str, lang="de")
                + " Uhr "
                + num2words(minute_str, lang="de")
            )
            return formatted_time
        number_str = match.group().replace(",", ".")
        number = float(number_str)
        if "€" in match.string or "$" in match.string:
            word = num2words(number, to="currency", lang="de")
        else:
            word = num2words(number, lang="de")
        return word

    # https://stackoverflow.com/questions/5917082/regular-expression-to-match-numbers-with-or-without-commas-and-decimals-in-text
    return re.sub(r"[$€]?(\d*[.,]?\d+(?:\sUhr)?)", callback, input_str)


def tts_conversation(conversation: str):
    # First separate the conversation into a list
    conversation_list = conversation.split("@@")

    # Have two voices for the conversation
    voices = random.sample(["alloy", "echo", "fable", "onyx", "nova", "shimmer"], k=2)

    conversation = AudioSegment.empty()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": "Given a conversation between two people, you should reply with a title that summarize in a few words what the subject is. ONLY reply with the title. KEEP the size small.",
            },
            {"role": "user", "content": " ".join(conversation_list)},
        ],
        max_tokens=12,
    )
    filename = response.choices[0].message.content
    filename = "".join(
        c for c in filename if c.isalpha() or c.isdigit() or c == " "
    ).rstrip()

    for i in range(len(conversation_list)):
        input_str = cloze_remover(conversation_list[i])
        input_str = replace_numbers(input_str)

        response = client.audio.speech.create(
            model="tts-1", voice=voices[i % 2], input=input_str
        )

        conversation += AudioSegment.from_mp3(io.BytesIO(response.content))
        if i != len(conversation_list):
            conversation += AudioSegment.silent(duration=600)

    output_filename = "output/" + "DE_Konversation_" + filename + ".mp3"
    conversation.export(output_filename, format="mp3")


def tts(input_str):
    input_str = cloze_remover(input_str)

    input_str = replace_numbers(input_str)

    print(input_str)

    voice = client.random_voice()

    filename_ai = make_filename(input_str, "DE", voice)
    output_folder_path = Path(__file__).parent / "output"
    speech_file_path = output_folder_path / filename_ai

    client.tts(input_str=input_str)

    client.write_to_file(speech_file_path)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Text to speech using OpenAI API")

    parser.add_argument("text", type=str, help="text that needs to be speech")
    parser.add_argument(
        "-C",
        "--client",
        choices=["azure", "openai"],
        default="azure",
        help="specify the text-to-speech service client (default: azure)",
    )
    parser.add_argument(
        "-c",
        "--conversation",
        action="store_true",
        help='treats text as conversation, separated by "@@"',
    )

    args = parser.parse_args()

    if args.client == "azure":
        AZURE_SPEECH_API_KEY = os.getenv("AZURE_SPEECH_API_KEY")
        client = AzureClient(service_key=AZURE_SPEECH_API_KEY)
    elif args.client == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = OpenAIClient(api_key=OPENAI_API_KEY)

    if args.conversation:
        tts_conversation(args.text)
    else:
        tts(args.text)