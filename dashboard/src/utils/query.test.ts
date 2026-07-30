import { describe, it, expect } from 'vitest';
import { AxiosError, HttpStatusCode } from 'axios';

import {
  DEFAULT_QUERY_RETRY_COUNT,
  isBadRequestError,
  retryHandler,
} from './query';

const createAxiosError = (status: number): AxiosError => {
  return new AxiosError(
    'Request failed',
    AxiosError.ERR_BAD_REQUEST,
    undefined,
    undefined,
    {
      status,
      statusText: 'Error',
      headers: {},
      config: {} as never,
      data: {},
    },
  );
};

describe('isBadRequestError', () => {
  it('returns true for Axios 400 errors', () => {
    expect(isBadRequestError(createAxiosError(HttpStatusCode.BadRequest))).toBe(
      true,
    );
  });

  it('returns false for Axios non-400 errors', () => {
    expect(
      isBadRequestError(createAxiosError(HttpStatusCode.InternalServerError)),
    ).toBe(false);
  });

  it('returns false for plain Error and non-error values', () => {
    expect(isBadRequestError(new Error('400:Bad request'))).toBe(false);
    expect(isBadRequestError('400')).toBe(false);
    expect(isBadRequestError(null)).toBe(false);
  });
});

describe('retryHandler', () => {
  it('defaults to DEFAULT_QUERY_RETRY_COUNT', () => {
    const shouldRetry = retryHandler();
    const error = new Error('500:Server error');

    expect(shouldRetry(DEFAULT_QUERY_RETRY_COUNT - 1, error)).toBe(true);
    expect(shouldRetry(DEFAULT_QUERY_RETRY_COUNT, error)).toBe(false);
  });

  it('does not retry on Axios 400 errors', () => {
    const shouldRetry = retryHandler();
    expect(shouldRetry(0, createAxiosError(HttpStatusCode.BadRequest))).toBe(
      false,
    );
  });

  it('still retries other Axios errors until the retry limit', () => {
    const shouldRetry = retryHandler();
    const error = createAxiosError(HttpStatusCode.InternalServerError);

    expect(shouldRetry(0, error)).toBe(true);
    expect(shouldRetry(DEFAULT_QUERY_RETRY_COUNT, error)).toBe(false);
  });
});
