# blaaaaaaa

from connexion.problem import problem


# Exceptions
class DatabaseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NotFoundInDB(Exception):
    def __init__(self, uuid):
        super().__init__(f" UUID '{uuid}' not found in DB.")


class IntegrityError(Exception):
    def __init__(self, uuid):
        super().__init__(f" UUID '{uuid}' already existing in DB.")


class GenericError(Exception):
    def __init__(self, message):
        super().__init__(message)


# Handlers
def not_found_handler(request, e):
    return problem(
            title="Not Found in DB",
            detail=str(e),
            status=404
        )


def integrity_error_handler(request, e):
    return problem(
        title="Integrity Error",
        detail=str(e),
        status=400
    )

def db_error_handler(request, e):
    return problem(
        title="Database Error",
        detail=str(e),
        status=500
    )


def generic_error_handler(request, e):
    return problem(
        title="Generic Error",
        detail=str(e),
        status=500
    )


