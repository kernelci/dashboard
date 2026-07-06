import { AxiosError, HttpStatusCode } from 'axios';

export const DEFAULT_QUERY_RETRY_COUNT = 3;

export const retryHandler = (retryCount: number | boolean = 3) => {
  return (failureCount: number, error: Error): boolean => {
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

export const isBadRequestError = (error: unknown): boolean => {
  if (error instanceof AxiosError) {
    return error.response?.status === HttpStatusCode.BadRequest;
  }

  if (error instanceof Error) {
    const statusCode = Number(error.message.split(':')[0]);
    return statusCode === HttpStatusCode.BadRequest;
  }

  return false;
};
