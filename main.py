import driver
from dotenv import load_dotenv
from os import getenv

def main():
        load_dotenv(dotenv_path="./venv/keys.env")
        session = driver.WebDriverSession()
        session.get("https://www.youtube.com")


if __name__ == "__main__":
        main()