import argparse

import requests
from bs4 import BeautifulSoup
import wget


def get_word_by_author(author, language_code="en"):
    # Set up the API endpoint
    api_url = "https://commons.wikimedia.org/w/api.php"

    # Set up parameters for the API request
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": f'author:"{author}"',
    }

    # Make the API request
    response = requests.get(api_url, params=params)
    data = response.json()

    # Check if there are search results
    if "query" in data and "search" in data["query"]:
        search_results = data["query"]["search"]
        if search_results:
            # Print information about the first search result
            result = search_results[0]
            print(f"Title: {result['title']}")
            print(f"Snippet: {result['snippet']}")
        else:
            print("No results found for the specified author.")
    else:
        print("Failed to retrieve search results.")


def download_wikipedia_audio(word):
    # Capitalize the word if not already capitalized
    word = word.capitalize()

    # Construct the Wikipedia URL
    wikipedia_url = f"https://en.wiktionary.org/wiki/{word}#German"

    # Send a GET request to the Wikipedia page
    response = requests.get(wikipedia_url)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the audio element

        audio_element = soup.find("a", class_="mw-tmh-play", href=True)
        if audio_element:
            # Get the href attribute
            audio_href = audio_element["href"]

            # Download the audio file
            audio_url = f"https://en.wiktionary.org{audio_href}"
            filename = f"{word}_audio.ogg"
            wget.download(audio_url, out=filename)
            print(f"Audio file '{filename}' downloaded successfully.")
        else:
            print(soup)
            print(audio_element)
            print("Audio element not found on the page.")
    else:
        print(f"Failed to retrieve Wikipedia page. Status code: {response.status_code}")


def generate_wikipedia_url(word: str):
    # Format the Wikipedia URL
    return f"https://en.wiktionary.org/wiki/{word.capitalize()}#German"


def remove_article(sentence: str):
    german_articles = [
        # Definite Articles
        "der",
        "die",
        "das",  # Masculine, Feminine, Neuter - Nominative
        "den",
        "die",
        "das",  # Masculine, Feminine, Neuter - Accusative
        "dem",
        "der",
        "dem",  # Masculine, Feminine, Neuter - Dative
        "des",
        "der",
        "des",  # Masculine, Feminine, Neuter - Genitive
        # Indefinite Articles
        "ein",
        "eine",
        "ein",  # Masculine, Feminine, Neuter - Nominative
        "einen",
        "eine",
        "ein",  # Masculine, Feminine, Neuter - Accusative
        "einem",
        "einer",
        "einem",  # Masculine, Feminine, Neuter - Dative
        "eines",
        "einer",
        "eines",  # Masculine, Feminine, Neuter - Genitive
    ]

    words = sentence.split()

    if len(words) == 2 and words[0].lower() in german_articles:
        return words[1]
    else:
        return sentence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract voice from wikipedia")
    parser.add_argument(
        "sentence", type=str, help="The sentence we want to extract the word from"
    )

    args = parser.parse_args()

    if not args.sentence:
        raise ValueError(
            "Input argument is missing. Please provide a command-line argument."
        )

    word = remove_article(args.sentence)
    download_wikipedia_audio(word)
    wiki_url = generate_wikipedia_url(word)
    print(wiki_url)
