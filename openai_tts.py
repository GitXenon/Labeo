import random

from openai import OpenAI


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


class OpenAIClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.response = None
        self.voice = "echo"

    def random_voice(self):
        self.voice = random.choice(
            ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        )
        return self.voice

    def tts(self, *, input_str: str):
        self.response = self.client.audio.speech.create(
            model="tts-1", voice=self.voice, input=input_str
        )

    def write_to_file(self, path: str):
        if self.response != None:
            self.response.write_to_file(path)
            print(f"{bcolors.OKGREEN}Success: Wrote response to {path}{bcolors.ENDC}")
            self.response = None
        else:
            print(
                f"{bcolors.WARNING}Warning: You need to call the function tts() before{bcolors.ENDC}"
            )
