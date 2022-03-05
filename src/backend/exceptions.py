class UnprocessableEntity(Exception):

    def __init__(self):
        super().__init__("Request can't be processed by any manga source.")
