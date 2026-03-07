
class AlreadySentOtpException(Exception):
    def __init__(self, message):
        super(AlreadySentOtpException,self).__init__(message)
        self.message = message

class MandatoryInputMissingException(Exception):
    def __init__(self, message):
        super(MandatoryInputMissingException,self).__init__(message)
        self.message = message








class InvalidOTPException(Exception):
    def __init__(self, message):
        super(InvalidOTPException,self).__init__(message)
        self.message = message


class AlreadySentOtpException(Exception):
    def __init__(self, message):
        super(AlreadySentOtpException,self).__init__(message)
        self.message = message

class MandatoryInputMissingException(Exception):
    def __init__(self, message):
        super(MandatoryInputMissingException,self).__init__(message)
        self.message = message

class NoOTPExistsException(Exception):
    def __init__(self, message):
        super(NoOTPExistsException,self).__init__(message)
        self.message = message

class InvalidOTPException(Exception):
    def __init__(self, message):
        super(InvalidOTPException,self).__init__(message)
        self.message = message

class InvalidOTPTypeException(Exception):
    def __init__(self, message):
        super(InvalidOTPTypeException,self).__init__(message)
        self.message = message

class OTPExpiredException(Exception):
    def __init__(self, message):
        super(OTPExpiredException,self).__init__(message)
        self.message = message
        
class UserNotFoundException(Exception):
    def __init__(self, message):
        super(UserNotFoundException,self).__init__(message)
        self.message = message
        
class InvalidUsernameFormatException(Exception):
    def __init___(self, message):
        super(InvalidUsernameFormatException, self).__init__(message)
        self.message = message