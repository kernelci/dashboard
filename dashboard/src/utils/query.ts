import { AxiosError, HttpStatusCode } from 'axios';

export const DEFAULT_QUERY_RETRY_COUNT = 3;

export const isBadRequestError = (error: unknown): boolean => {
  return (
    error instanceof AxiosError &&
    error.response?.status === HttpStatusCode.BadRequest
  );
};

export const retryHandler = (
  retryCount: number | boolean = DEFAULT_QUERY_RETRY_COUNT,
) => {
  return (failureCount: number, error: Error): boolean => {
    if (isBadRequestError(error)) {
      return false;
    }

    const splittedError = error.message.split(':');
    if (
      splittedError &&
      splittedError.length > 1 &&
      splittedError[0] === '200'
    ) {
      return false;
    }

    if (typeof retryCount === 'boolean') {
      return retryCount;
    }

    if (typeof retryCount === 'number' && failureCount >= retryCount) {
      return false;
    }
    return true;
  };
};
