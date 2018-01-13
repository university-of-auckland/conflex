from settings import *
from confluence.api import ConfluenceAPI


if __name__ == '__main__':
    # Confluence Server Address takes precedence over URL if present.
    api = ConfluenceAPI(confluence_api_url, confluence_api_user, confluence_api_pass)