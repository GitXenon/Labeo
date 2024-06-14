import requests
from .colors import bcolors

class DeeplTranslateClient:

    def __init__(self, api_key: str, source_lang: str, target_lang: str):
        self.api_key = api_key
        self.source_lang = source_lang.capitalize()
        self.target_lang = target_lang.capitalize()

    def translate(self, text: str):
        DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"

        headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TTS/0.1"
        }

        body = {"text": [text], "target_lang": self.target_lang ,"source_lang": self.source_lang}

        response = requests.post(DEEPL_ENDPOINT, headers=headers, json=body)

        if response.status_code == 200:
            translated_text: str = response.json()['translations'][0]['text']
            return translated_text
        else:
            print(
                f"{bcolors.FAIL}Error {response.status_code}: {response.text}{bcolors.ENDC}"
            )
            return None