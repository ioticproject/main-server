from http import HTTPStatus


def hello():
    pass


class EmailOperationError(RuntimeError):
    def __init__(self):
        self.message = 'Could not send the confirmation of account email.'

    @property
    def status_code(self):
        return HTTPStatus.CREATED
