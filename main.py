import argparse
import re
import os
import uuid

import requests
from dotenv import load_dotenv
from pathlib import Path
from num2words import num2words

from openai_tts import OpenAIClient
from azure_tts import AzureClient


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def cloze_remover(cloze_string: str):
    return re.sub(r"\{\{\w*::(.*?)(::.*?)?\}\}", r"\1", cloze_string)


def is_conversation(text: str):
    return True if re.search("\W - [A-Z]", text) else False


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
            try:
                hour_str, minute_str = time_str.split(".")
            except ValueError:
                hour_str, minute_str = time_str, "null"
            if minute_str == "null":
                formatted_time = num2words(hour_str, lang="de") + " Uhr"
            else:
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


def translate(text: str):
    AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com/translate"
    AZURE_TRANSLATION_API_KEY = os.getenv("AZURE_TRANSLATION_API_KEY")

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATION_API_KEY,
        "Content-Type": "application/json; charset=UTF-8",
        "Ocp-Apim-Subscription-Region": "westeurope",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    params = {"api-version": "3.0", "from": "de", "to": "en"}

    body = [{"text": text}]

    response = requests.post(AZURE_ENDPOINT, params=params, headers=headers, json=body)

    if response.status_code == 200:
        translated_text = response.json()[0]["translations"][0]["text"]
        return translated_text
    else:
        print(
            f"{bcolors.FAIL}Error {response.status_code}: {response.text}{bcolors.ENDC}"
        )
        return None


def tts(input_str):
    input_str = cloze_remover(input_str)

    input_str = replace_numbers(input_str)

    print(input_str)
    print(translate(input_str))

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
    args = parser.parse_args()

    if args.client == "azure":
        AZURE_SPEECH_API_KEY = os.getenv("AZURE_SPEECH_API_KEY")
        client = AzureClient(service_key=AZURE_SPEECH_API_KEY)
    elif args.client == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = OpenAIClient(api_key=OPENAI_API_KEY)

    tts(args.text)
