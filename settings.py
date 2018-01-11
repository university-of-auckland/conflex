from os.path import join, dirname

import os
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

if os.environ.get("CONFLUENCE_API_SERVER"):
    confluence_api_url = os.environ.get("CONFLUENCE_API_SERVER")
else:
    confluence_api_url = os.environ.get("CONFLUENCE_API_URL")

confluence_api_user = os.environ.get("CONFLUENCE_API_USER")
confluence_api_pass = os.environ.get("CONFLUENCE_API_PASS")