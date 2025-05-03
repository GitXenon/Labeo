import argparse
import re
import os
from num2words import num2words

from dotenv import load_dotenv
from pathlib import Path

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


def replace_numbers(input_str: str) -> str:
    """
    Replace numeric representations in German text with their word equivalents.

    Args:
        input_str: The input string containing numbers to replace

    Returns:
        String with numbers replaced by words
    """
    if not input_str:
        return input_str

    # Helper function to clean German number format
    def clean_number(num_str):
        # Replace German thousands separator
        cleaned = num_str.replace(".", "")
        # Replace German decimal separator with dot for processing
        cleaned = cleaned.replace(",", ".")
        return cleaned

    # Process dates (DD.MM.YYYY)
    date_pattern = r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b"

    def replace_date(match):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        day_str = num2words(day, lang="de", to="ordinal")
        month_str = num2words(month, lang="de")
        year_str = num2words(year, lang="de", to="year")
        return f"{day_str} {month_str} {year_str}"

    input_str = re.sub(date_pattern, replace_date, input_str)

    # Process times (HH.MM Uhr)
    time_pattern = r"\b(\d{1,2})\.(\d{2}) Uhr\b"

    def replace_time(match):
        hour = int(match.group(1))
        minute = int(match.group(2))
        hour_str = num2words(hour, lang="de")
        minute_str = num2words(minute, lang="de")
        return f"{hour_str} Uhr {minute_str}"

    input_str = re.sub(time_pattern, replace_time, input_str)

    # Process Euro currency
    euro_pattern = r"(\d+(?:[,.]\d+)?) €"

    def replace_euro(match):
        amount = clean_number(match.group(1))
        return num2words(float(amount), lang="de", to="currency", currency="EUR")

    input_str = re.sub(euro_pattern, replace_euro, input_str)

    # Process Dollar currency
    dollar_pattern = r"(\d+(?:[,.]\d+)?) \$"

    def replace_dollar(match):
        amount = float(clean_number(match.group(1)))
        return f"{num2words(amount, lang='de')} Dollar"

    input_str = re.sub(dollar_pattern, replace_dollar, input_str)

    # Process percentages
    percentage_pattern = r"(\d+(?:[,.]\d+)?)%"

    def replace_percentage(match):
        number = clean_number(match.group(1))
        if "." in number:
            int_part, dec_part = number.split(".")
            return f"{num2words(int(int_part), lang='de')} Komma {num2words(int(dec_part), lang='de')} Prozent"
        else:
            return f"{num2words(int(number), lang='de')} Prozent"

    input_str = re.sub(percentage_pattern, replace_percentage, input_str)

    # Process phone numbers
    phone_pattern = r"\b(\d{4}) (\d{6})\b"

    def replace_phone(match):
        digits = match.group(1) + match.group(2)
        return " ".join(num2words(int(digit), lang="de") for digit in digits)

    input_str = re.sub(phone_pattern, replace_phone, input_str)

    # Process fractions
    fraction_pattern = r"\b(\d+)/(\d+)\b"

    def replace_fraction(match):
        numerator = int(match.group(1))
        denominator = int(match.group(2))

        # Special case for common fractions
        if numerator == 1 and denominator == 4:
            return "ein Viertel"
        elif numerator == 1 and denominator == 2:
            return "ein halb"
        else:
            numerator_str = num2words(numerator, lang="de")
            denominator_str = num2words(denominator, lang="de")
            return f"{numerator_str}/{denominator_str}"

    input_str = re.sub(fraction_pattern, replace_fraction, input_str)

    # Process mixed numbers
    mixed_pattern = r"\b(\d+) (\d+)/(\d+)\b"

    def replace_mixed(match):
        whole = int(match.group(1))
        numerator = int(match.group(2))
        denominator = int(match.group(3))

        whole_str = num2words(whole, lang="de")

        # Special case for 1/2
        if numerator == 1 and denominator == 2:
            return f"{whole_str} einhalb"
        else:
            fraction_str = (
                num2words(numerator, lang="de")
                + "/"
                + num2words(denominator, lang="de")
            )
            return f"{whole_str} {fraction_str}"

    input_str = re.sub(mixed_pattern, replace_mixed, input_str)

    # Process mathematical expressions
    math_pattern = r"(\d+) ([+\-*/=]) (\d+)"

    def replace_math(match):
        first = int(match.group(1))
        operator = match.group(2)
        second = int(match.group(3))

        first_str = num2words(first, lang="de")
        second_str = num2words(second, lang="de")

        operator_words = {
            "+": "plus",
            "-": "minus",
            "*": "mal",
            "/": "geteilt durch",
            "=": "gleich",
        }

        return f"{first_str} {operator_words.get(operator, operator)} {second_str}"

    input_str = re.sub(math_pattern, replace_math, input_str)

    # Process years (standalone 4-digit numbers that might be years)
    year_pattern = r"\b(19\d{2}|20\d{2})\b"

    def replace_year(match):
        year = int(match.group(1))
        return num2words(year, lang="de", to="year")

    input_str = re.sub(year_pattern, replace_year, input_str)

    # Process ordinal numbers
    ordinal_pattern = r"\b(\d+)\."

    def replace_ordinal(match):
        number = int(match.group(1))
        return num2words(number, lang="de", to="ordinal")

    input_str = re.sub(ordinal_pattern, replace_ordinal, input_str)

    # Process decimal numbers
    decimal_pattern = r"\b-?(\d+),(\d+)\b"

    def replace_decimal(match):
        int_part = match.group(1)
        dec_part = match.group(2)
        prefix = "minus " if int_part.startswith("-") else ""
        int_part = int_part.lstrip("-")
        int_str = num2words(int(int_part), lang="de")
        dec_str = num2words(int(dec_part), lang="de")
        return f"{prefix}{int_str} Komma {dec_str}"

    input_str = re.sub(decimal_pattern, replace_decimal, input_str)

    # Process negative numbers
    negative_pattern = r"\b-(\d+)\b"

    def replace_negative(match):
        number = int(match.group(1))
        return f"minus {num2words(number, lang='de')}"

    input_str = re.sub(negative_pattern, replace_negative, input_str)

    # Process large numbers with thousand separators
    large_pattern = r"\b(\d{1,3}(?:\.\d{3})+)\b"

    def replace_large(match):
        number = clean_number(match.group(1))
        return num2words(int(number), lang="de")

    input_str = re.sub(large_pattern, replace_large, input_str)

    # Process any remaining cardinal numbers
    cardinal_pattern = r"\b\d+\b"

    def replace_cardinal(match):
        return num2words(int(match.group(0)), lang="de")

    input_str = re.sub(cardinal_pattern, replace_cardinal, input_str)

    return input_str


def tts(input_str: str):
    parsed_input_str = cloze_remover(input_str)

    text_str = replace_numbers(parsed_input_str)

    print(text_str)
    translation = translate_client.translate(text_str)
    print(translation)

    voice = tts_client.random_voice()

    filename_ai = make_filename(text_str, "DE", voice)
    output_folder_path = Path(__file__).parent / "output"
    speech_file_path = output_folder_path / filename_ai

    tts_client.tts(input_str=text_str)

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
        help="specify the translation service client (default: deepl)",
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
            raise ValueError("Deepl API key is missing in the environment variables")
        translate_client = DeeplTranslateClient(
            api_key=DEEPL_API_KEY, source_lang="de", target_lang="en"
        )
    elif args.translator == "azure":
        AZURE_TRANSLATION_API_KEY = os.getenv("AZURE_TRANSLATION_API_KEY")
        if not AZURE_TRANSLATION_API_KEY:
            raise ValueError(
                "Azure Translation API key is missing in the environment variables"
            )
        translate_client = AzureTranslateClient(
            api_key=AZURE_TRANSLATION_API_KEY, source_lang="de", target_lang="en"
        )

    tts(args.text)
