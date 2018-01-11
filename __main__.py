from settings import *
from util.confluence_api import ConfluenceAPI


# Main Capsule File
def main():
    # Confluence Server Address takes precedence over URL if present.
    api = ConfluenceAPI(confluence_api_url, confluence_api_user, confluence_api_pass)


if __name__ == '__main__':
    # Execute only if run as a script
    main()
