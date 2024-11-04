from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse


def parseIntervalInDaysGetParameter(intervalInDays: str) -> int:
    try:
        parsedIntervalInDays = int(intervalInDays)
        if parsedIntervalInDays < 1:
            raise ExceptionWithJsonResponse(
                "Invalid intervalInDays, must be bigger than 0", 400
            )
        return parsedIntervalInDays
    except ValueError:
        raise ExceptionWithJsonResponse("Invalid intervalInDays, must be a number", 400)
