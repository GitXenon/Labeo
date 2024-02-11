# TTS
A small program to help me create audio for my Anki cards to practice German.

## Usage

Run `python openai_tts.py --help` to learn how to use this program. The other files are not really used for now.

## Setup
You need an OpenAI API key for this program. When you have this, create a `.env` file in the root folder like this:
```
OPENAI_API_KEY=<OPENAI_API_KEY>
```

## TODO
[] Add the ability to add pauses, like [1sec] would add to the .mp3 1 second pause. This could be hard when in the middle of a sentence.
[] Add the possibility to have a conversation, maybe two inputs would create a conversation then could export to two files or could merge into one.
[] Complete wikipedia fetching of pronounciation or help to automate the process. Right now I'm searching for the word, then I find the audio file which I find the best (author is ???) then I put it with the card.