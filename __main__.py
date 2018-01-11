from os.path import join, dirname
from dotenv import load_dotenv
from util.confluence_api import ConfluenceAPI

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Main Capsule File
def main():
    """Summary line.

    Extended description of function.

    Args:
        arg1 (int): Description of arg1
        arg2 (str): Description of arg2

    Returns:
        bool: Description of return value

    """
    hello = ConfluenceAPI()
    print("hello")


if __name__ == '__main__':
    # execute only if run as a script
    main()
