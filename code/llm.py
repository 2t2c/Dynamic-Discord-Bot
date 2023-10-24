"""
LLaMA CPP Language Model Wrapper

Usage:
1. Create an instance of the 'LLM' class.
2. Use the 'generate' method to generate responses based on user prompts.

Example:
llm_obj = LLM()
response = llm_obj.generate("Translate the following text into French: 'Hello, world!'")
"""
import os

# imports
from langchain.llms import LlamaCpp
import re
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from .scraper import WebScraper
import logging

# fetch logger
logger = logging.getLogger("discord_bot_logger")

# creating global scraper instance
scraper_obj = WebScraper()

# callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# fetch LLM model path
LLM_PATH = os.getenv("LLM_PATH")

class LLM:
    """
    Main class load and infer LLM generations
    """
    def __init__(self):
        self.max_prompt_length = 512
        # loading the model locally
        self.llm = LlamaCpp(
            model_path=LLM_PATH, # local path
            temperature=0.75,
            top_p=1,
            callback_manager=callback_manager,
            verbose=False,
            n_gpu_layers=-1,
            echo=False,
            streaming=False
        )

    def prompt_formatter(self, prompt):
        """
        Method to format the input prompt

        :param:
            prompt: string
            llm input human prompt
        :return:
        """
        formatted_prompt = re.sub("(!ask|!summarize)", "", prompt, re.IGNORECASE).strip()
        return formatted_prompt

    def generate(self, prompt, action):
        """
        Method to generate the answer for a given query
        :param:
            prompt: string
            llm input human prompt
        :param:
            action: string
            type of action to perform
        :return:
            response: string
            llm generate response
        """
        # format the prompt
        formatted_prompt = self.prompt_formatter(prompt)
        # scrape content for quick summarization
        if action=="summary":
            scraped_content = scraper_obj.scrape_content(formatted_prompt)
            if scraped_content:
                formatted_prompt += " " + scraped_content

        # generate response
        return self.llm(formatted_prompt[:self.max_prompt_length])

