from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from dotenv import load_dotenv
from os import getenv

def main():
        load_dotenv(dotenv_path="./venv/keys.env")
        # driver = webdriver.Chrome()
        print("test3")
        i = input("input 1: ")
        print("input 1: {}".format(i))


if __name__ == "__main__":
        print("test2")
        main()