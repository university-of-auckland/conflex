class ConfluenceAPI(object):
    """Confluence API Class

    This class acts as an API bridge between python and the confluence API. The class is designed as a singleton
    meaning that only one instance of the class is ever created.
    """
    __instance = None

    def __new__(cls, url, username, password):
        """Create new class instance

        This method will create a new instance of the current class if it does not already exist, otherwise it will
        return the current instance of the class.
        """

        if ConfluenceAPI.__instance is None:
            ConfluenceAPI.__instance = object.__new__(cls)
            ConfluenceAPI.__instance.url = url
            ConfluenceAPI.__instance.username = username
            ConfluenceAPI.__instance.password = password
        return ConfluenceAPI.__instance

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
