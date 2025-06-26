class BaseError(Exception):
    def __init__(self, status_code: int, message: str, previous_url: str):
        super().__init__()
        self.status_code = status_code
        self.message = message
        self.previous_url = previous_url


class ContentNotFoundError(BaseError):
    def __init__(self, message: str='Sorry! Page Doesn\'t Exists', previous_url: str='/'):
        super().__init__(status_code=404, message=message, previous_url=previous_url)
        

class InternalServerError(BaseError):
    def __init__(self, message: str='Sorry! Problem Occurred at Our End', previous_url: str='/'):
        super().__init__(status_code=500, message=message, previous_url=previous_url)
        

class NotAuthorizedError(BaseError):
    def __init__(self, message: str='Hmm. You\'re not Authorized', previous_url: str='/'):
        super().__init__(status_code=401, message=message, previous_url=previous_url)
        

class ForbiddenError(BaseError):
    def __init__(self, message: str='Sorry! Cannot Allow to Proceed', previous_url: str='/'):
        super().__init__(status_code=403, message=message, previous_url=previous_url)
        

class MethodNotAllowedError(BaseError):
    def __init__(self, message: str='Sorry! Request Method is not Allowed', previous_url: str='/'):
        super().__init__(status_code=405, message=message, previous_url=previous_url)
        