import random

import requests


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


class AzureClient:
    TTS_ENDPONT = "https://westeurope.tts.speech.microsoft.com/cognitiveservices/v1"
    XML_TEMPLATE = """<speak version='1.0' xml:lang='de-DE'>
    <voice xml:lang='de-DE' xml:gender='Male'
        name='{voice}'>
            {text}
    </voice></speak>"""

    def __init__(self, service_key):
        self.service_key = service_key
        self.voice = "de-DE-ConradNeural"
        self.response = None

    def random_voice(self):
        voice = random.choice(
            [
                "de-DE-ChristophNeural",
                "de-DE-ConradNeural",
                "de-DE-ElkeNeural",
                "de-DE-KlarissaNeural",
                "de-DE-SeraphinaMultilingualNeural",
                "de-DE-FlorianMultilingualNeural",
            ]
        )
        self.voice = voice
        return voice

    def tts(self, *, input_str: str):
        headers = {
            'Ocp-Apim-Subscription-Key': self.service_key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'tts-deutsch'
        }
        data = self.XML_TEMPLATE.format(voice=self.voice, text=input_str)

        response = requests.post(self.TTS_ENDPONT, data=data, headers=headers)
        self.response = response

    def write_to_file(self, filepath: str):
        if self.response != None:
            with open(filepath, mode="wb") as f:
                f.write(self.response.content)
            print(f"{bcolors.OKGREEN}Success: Wrote response to {filepath}{bcolors.ENDC}")
            self.response = None

        else:
            print(
                f"{bcolors.WARNING}Warning: You need to call the function tts() before{bcolors.ENDC}"
            )
