from settings import *


class ConfluenceAPI(object):
    """Confluence API Class

    This class acts as an API bridge between python and the confluence API.
    """

    # Private attributes of the API class.
    url = config['confluence']['host']
    port = config['confluence']['port']
    __username = config['confluence']['username']
    __password = config['confluence']['password']

    def get_info(self):
        """Summary line.

        Extended description of function.

        Args:
            arg1 (int): Description of arg1
            arg2 (str): Description of arg2

        Returns:
            bool: Description of return value

        """
        return self.url
