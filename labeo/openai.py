import random

from openai import OpenAI

from .colors import bcolors


class OpenAITTSClient:
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
