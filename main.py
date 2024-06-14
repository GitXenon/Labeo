import argparse
import re
import os

from dotenv import load_dotenv
from pathlib import Path
from num2words import num2words

from labeo.deepl import DeeplTranslateClient
from labeo.openai import OpenAITTSClient
from labeo.azure import AzureTTSClient, AzureTranslateClient


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
    

def format_time_string(time_str: str) -> str:
    """Format a time string in German.

    This function takes a time string, splits it into hours and minutes, 
    converts them to words in German, and then formats them accordingly.

    Args:
        time_str (str): The time string to format, e.g., '13.45' or '13'.

    Returns:
        str: The formatted time string in German.
    """
    try:
        hour_str, minute_str = time_str.split(".")
    except ValueError:
        hour_str, minute_str = time_str, "null"
    
    if minute_str == "null":
        formatted_time = num2words(hour_str, lang="de") + " Uhr"
    else:
        formatted_time = (
            num2words(hour_str, lang="de") + " Uhr " + num2words(minute_str, lang="de")
        )
    
    return formatted_time


def replace_numbers(input_str: str):
    """Replace numbers in a string with their word equivalents in German.

    This function looks for numbers in the input string and replaces them 
    with their corresponding words in German. It handles numbers that represent
    time (with 'Uhr') and currency (Euro or Dollar).

    Args:
        input_str (str): The input string containing numbers.

    Returns:
        str: The input string with numbers replaced by words in German.
    """
    def _callback(match: re.Match):
        matched_str = match.group()
        if "Uhr" in matched_str:
            time_str: str = matched_str.replace(" Uhr", "")
            return format_time_string(time_str)

        number_str = match.group().replace(",", ".")
        number = float(number_str)
        if "€" in match.string or "$" in match.string:
            word = num2words(number, to="currency", lang="de")
        else:
            word = num2words(number, lang="de")
        return word

    # https://stackoverflow.com/questions/5917082/regular-expression-to-match-numbers-with-or-without-commas-and-decimals-in-text
    return re.sub(r"[$€]?(\d*[.,]?\d+(?:\sUhr)?)", _callback, input_str)


def tts(input_str: str):
    input_str = cloze_remover(input_str)

    input_str = replace_numbers(input_str)

    print(input_str)
    print(translate_client.translate(input_str))

    voice = tts_client.random_voice()

    filename_ai = make_filename(input_str, "DE", voice)
    output_folder_path = Path(__file__).parent / "output"
    speech_file_path = output_folder_path / filename_ai

    tts_client.tts(input_str=input_str)

    tts_client.write_to_file(speech_file_path)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Text-to-Speech Helper")

    parser.add_argument("text", type=str, help="text that needs to be speech")
    parser.add_argument(
        "-C",
        "--client",
        choices=["azure", "openai"],
        default="azure",
        help="specify the text-to-speech service client (default: azure)",
    )
    parser.add_argument(
        "-T",
        "--translator",
        choices=["azure", "deepl"],
        default="deepl",
        help="specify the translation service client (default: deepl)"
    )
    args = parser.parse_args()

    if args.client == "azure":
        AZURE_SPEECH_API_KEY = os.getenv("AZURE_SPEECH_API_KEY")
        if not AZURE_SPEECH_API_KEY:
            raise ValueError(
                "Azure Speech API key is missing in the environment variables"
            )
        tts_client = AzureTTSClient(service_key=AZURE_SPEECH_API_KEY)
    elif args.client == "openai":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is missing in the environment variables")
        tts_client = OpenAITTSClient(api_key=OPENAI_API_KEY)

    if args.translator == "deepl":
        DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
        if not DEEPL_API_KEY:
            raise ValueError(
                "Deepl API key is missing in the environment variables"
            )
        translate_client = DeeplTranslateClient(api_key=DEEPL_API_KEY, source_lang="de", target_lang="en")
    elif args.translator == "azure":
        AZURE_TRANSLATION_API_KEY = os.getenv("AZURE_TRANSLATION_API_KEY")
        if not AZURE_TRANSLATION_API_KEY:
            raise ValueError("Azure Translation API key is missing in the environment variables")
        translate_client = AzureTranslateClient(api_key=AZURE_TRANSLATION_API_KEY, source_lang="de", target_lang="en")

    tts(args.text)
