import type { AxiosRequestConfig } from 'axios';

import type { ResponseData } from '@/types/general';

import http from './api';

export class ApiError extends Error {
  constructor(
    message: string,
    readonly data: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class RequestData {
  static async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await http.get<ResponseData<T>>(url, config);

    if (res.data.error) {
      throw new ApiError(`${res.status}:${res.data.error}`, res.data);
    }

    return res.data;
  }

  static async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> {
    const res = await http.post<ResponseData<T>>(url, data, config);

    if (res.data.error) {
      throw new ApiError(`${res.status}:${res.data.error}`, res.data);
    }

    return res.data;
  }
}
