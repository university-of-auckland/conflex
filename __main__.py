from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Main Capsule File
def main():
    print("hello")


if __name__ == '__main__':
    # execute only if run as a script
    main()
