# LabeoLabel

<p><img src="https://badgen.net/static/python/3.12" alt="python version"> <a href="https://github.com/GitXenon/tts/blob/main/LICENSE"><img src="https://badgen.net/github/license/GitXenon/tts" alt="License"></a></p>
A small program to help me create audio for my Anki cards to practice German.

## Usage

Run `python main.py --help` to learn how to use this program.

```bash
python main.py "Hallo Welt!"
# Hallo Welt!
# Hello world!
# Success: Wrote response to ./output/de-DE-FlorianMultilingualNeural_Hallo_Welt.mp3
```

## Install

**TTS**: Depending on your preference, you will need either an [Azure Speech API key](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech) or an [OpenAI API key](https://platform.openai.com/docs/overview).

**Translation**: You can use [Azure Translation API key](https://learn.microsoft.com/en-us/azure/ai-services/translator/) for translation or [DeepL](https://developers.deepl.com/docs).

Azure has free tier options for both of the products and have given me better accuracy with German pronounciation. OpenAI has the tendancy of pronounciating in English on certain words.
When you have the necessary keys, create a `.env` file in the root folder with the following content:

```
OPENAI_API_KEY="<OPENAI_API_KEY>"
AZURE_SPEECH_API_KEY="<AZURE_SPEECH_API_KEY>"
AZURE_TRANSLATION_API_KEY="<AZURE_TRANSLATION_API_KEY>"
DEEPL_API_KEY="<DEEPL_API_KEY>"
```
