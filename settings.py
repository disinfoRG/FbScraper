from dotenv import load_dotenv
load_dotenv()
import os

CHROMEDRIVER_BIN = os.getenv("CHROMEDRIVER_BIN")
FIREFOXDRIVER_BIN = os.getenv("FIREFOXDRIVER_BIN")
DATABASE_URL = os.getenv("DATABASE_URL")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
FB_EMAIL = os.getenv("FB_EMAIL")
FB_PASSWORD = os.getenv("FB_PASSWORD")
USER = os.getenv("USER")
ROOT_FOLDER_PATH = os.getenv("ROOT_FOLDER_PATH")