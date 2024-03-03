import time
import json
import random
import re

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


class UnsupportedModelException(Exception):
    """Exception raised for unsupported models."""
    def __init__(self, model, message="Model not supported"):
        self.model = model
        self.message = message
        super().__init__(self.message)

class UnsupportedModeException(Exception):
    """Exception raised for unsupported modes."""
    def __init__(self, mode, message="Mode not supported"):
        self.mode = mode
        self.message = message
        super().__init__(self.message)

def text_to_chunks(text, chunk_approx_tokens=200000, avg_token_length=3):
    """
    Split the text into chunks, each approximating a certain number of tokens.

    :param text: The input text to be split into chunks.
    :param chunk_approx_tokens: The approximate number of tokens desired per chunk.
    :param avg_token_length: The estimated average length of a token, including spaces.
    :return: A list of text chunks.
    """
    # Estimate the number of characters per chunk to approximate the desired number of tokens
    chunk_approx_chars = chunk_approx_tokens * avg_token_length

    # Initialize an empty list to store the chunks
    chunks = []

    # Calculate the total length of the text
    text_length = len(text)

    # Initialize the start index for slicing the text
    start_index = 0

    # Loop to split the text into chunks
    while start_index < text_length:
        # Calculate the end index for the current chunk
        end_index = min(start_index + chunk_approx_chars, text_length)

        # Slice the text to create a chunk
        chunk = text[start_index:end_index]

        # Add the chunk to the list
        chunks.append(chunk)

        # Update the start index for the next chunk
        start_index = end_index

    return chunks


def find_first_url(text):
    # Regular expression pattern for matching URLs
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    match = re.search(pattern, text)
    if match:
        return match.group()
    else:
        return None


def setup_driver():
    # Initialize Chrome Options
    chrome_options = Options()
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up driver with options
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def send_to_anthropic(text_chunk, instructions):
    anthropic = Anthropic()

    completion = anthropic.completions.create(
        model="claude-2.1",
        max_tokens_to_sample=200000,
        prompt=f"{HUMAN_PROMPT} {instructions}:\n{text_chunk}{AI_PROMPT}",
    )

    return completion.completion


def send_to_AI(url, instructions, model, mode="text"):
    driver = setup_driver()
    
    driver.get(url)

    time.sleep(5)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    if mode=="text":
        text = driver.execute_script("return document.body.innerText")
    elif mode=="source":
        text = driver.page_source
    else:
        raise UnsupportedModeException(mode)
    
    print("---------------SCRAPE-RESULT----------------------")
    print("--------------------------------------------------")
    print(text)
    print("--------------------------------------------------")
    print("--------------------------------------------------")

    if model=="Claude 2":
        chunks = text_to_chunks(text,125000)
        summary = send_to_anthropic(chunks[0], instructions)
    else:
        raise UnsupportedModelException(model)

    print(summary)

    # Clean up
    driver.quit()

if __name__ == "__main__":
    
    with open('sources.json', 'r') as file:
        data = json.load(file)

    random.shuffle(data)

    for item in data:
        name = item.get("name", "N/A")  # Default to "N/A" if key doesn't exist
        language = item.get("language", "N/A")
        flag = item.get("flag", "N/A")
        source = item.get("source", "N/A")
        url = item.get("url", "N/A")
        model = item.get("model", "N/A")
        finder = item.get("finder", "N/A")
        summarizer = item.get("summarizer", "N/A")

        print(f"Name: {name}, Language: {language}, Flag: {flag}")
        print(f"Source: {source}, URL: {url}")
        print(f"Model: {model}")
        print(f"Finder: {finder}")
        print(f"Summarizer: {summarizer}")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("--------------------------------------------------")

        best_url = find_first_url(send_to_AI(url,finder,model,"source"))
        
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print(best_url)
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
    
    #TODO use an html template here and output it
    print("Done")

