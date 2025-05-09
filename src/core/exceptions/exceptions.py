class BusinessException(Exception):
    """
    Exception raised for Business related errors.

    Attributes:
        code -- integer error code
        description -- error description
    """

    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description
        super().__init__(f'BusinessException: {self.code}, {self.description}')
