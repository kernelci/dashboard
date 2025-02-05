import type { AxiosRequestConfig } from 'axios';

import type { ResponseData } from '@/types/general';

import http from './api';

export class RequestData {
  static async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await http.get<ResponseData<T>>(url, config);

    if (res.data.error) {
      throw new Error(res.data.error);
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
      throw new Error(res.data.error);
    }

    return res.data;
  }
}
