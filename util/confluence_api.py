class ConfluenceAPI:
    """Summary line.

    Extended description of function.

    Args:
        arg1 (int): Description of arg1
        arg2 (str): Description of arg2

    Returns:
        bool: Description of return value

    """

    __instance = None

    def __new__(cls, val):
        if ConfluenceAPI.__instance is None:
            ConfluenceAPI.__instance = object.__new__(cls)
        ConfluenceAPI.__instance.val = val
        return ConfluenceAPI.__instance

    # Class Variables.
    # hello = 'test'
    #
    # def __init__(cls, self):
    #     # Instance Variables.
    #     self.hello = 'test'
