# TTS

A small program to help me create audio for my Anki cards to practice German.

## Usage

Run `python main.py --help` to learn how to use this program. The other files are not really used for now.

## Setup

Depending on your preference, you will need either an [Azure Speech API key](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech) or an [OpenAI API key](https://platform.openai.com/docs/overview). The [Azure Translation API key](https://learn.microsoft.com/en-us/azure/ai-services/translator/) is for translation and is mandatory for now.
Azure has free tier options for both of the products and have given me better accuracy with German pronounciation. OpenAI has the tendancy of pronounciating in English on certain words.
When you have the necessary keys, create a `.env` file in the root folder with the following content:

```
OPENAI_API_KEY=<OPENAI_API_KEY>
AZURE_SPEECH_API_KEY="<AZURE_SPEECH_API_KEY>"
AZURE_TRANSLATION_API_KEY="<AZURE_TRANSLATION_API_KEY>"
```
