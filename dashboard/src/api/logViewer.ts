import pako from 'pako';
import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { minutesToMilliseconds } from 'date-fns';
import { useIntl } from 'react-intl';

import { AxiosError, HttpStatusCode } from 'axios';

import { LOG_EXCERPT_ALLOWED_DOMAINS } from '@/utils/constants/log_excerpt_allowed_domain';

import { RequestData } from './commonRequest';

// eslint-disable-next-line no-magic-numbers
const STALE_DURATION_MS = minutesToMilliseconds(60);

type FetchAndDecompressLogsResponse = {
  content: string;
};

const isGzipBytes = (data: Uint8Array): boolean =>
  // eslint-disable-next-line no-magic-numbers
  data.length >= 2 && data[0] === 0x1f && data[1] === 0x8b;

async function fetchAndDecompressLog(
  url: string,
): Promise<FetchAndDecompressLogsResponse> {
  const proxyUrl = `/api/proxy/?url=${encodeURIComponent(url)}`;

  try {
    const response = await RequestData.get<ArrayBuffer>(proxyUrl, {
      responseType: 'arraybuffer',
    });

    let byteResponse = new Uint8Array(response);
    const textDecoder = new TextDecoder('utf-8');

    while (isGzipBytes(byteResponse)) {
      byteResponse = pako.inflate(byteResponse);
    }

    return { content: textDecoder.decode(byteResponse) };
  } catch (error) {
    console.error(error);

    if (
      error instanceof AxiosError &&
      error.response?.status === HttpStatusCode.Forbidden
    ) {
      throw new Error('403:Domain not allowed');
    }

    throw new Error(
      `Failed to fetch logs: ${error instanceof Error ? error.message : 'Unknown error'}`,
    );
  }
}

export const useLogViewer = (
  url: string,
): UseQueryResult<FetchAndDecompressLogsResponse> => {
  return useQuery({
    queryKey: ['logs', url],
    queryFn: () => fetchAndDecompressLog(url),
    enabled: !!url,
    staleTime: STALE_DURATION_MS,
    refetchOnWindowFocus: false,
  });
};

const isAllowedUrl = (value: string): boolean => {
  try {
    const url = new URL(value);
    return LOG_EXCERPT_ALLOWED_DOMAINS.includes(url.hostname);
  } catch {
    return false;
  }
};

const fetchLogExcerptContent = async (
  logExcerpt: string | null | undefined,
  errorMessage: string,
): Promise<{ content: string }> => {
  if (!logExcerpt) {
    return { content: '' };
  }

  if (!isAllowedUrl(logExcerpt)) {
    return { content: logExcerpt };
  }

  try {
    const content = await fetchAndDecompressLog(logExcerpt);
    return content;
  } catch {
    return { content: errorMessage };
  }
};

export const useLogExcerpt = (
  logExcerpt?: string,
): UseQueryResult<{ content: string }> => {
  const { formatMessage } = useIntl();
  const errorMessage = formatMessage(
    { id: 'logViewer.errorFetchingLogExcerpt' },
    { logExcerpt },
  );
  return useQuery({
    queryKey: ['logExcerpt', logExcerpt, errorMessage],
    queryFn: () => fetchLogExcerptContent(logExcerpt, errorMessage),
    staleTime: STALE_DURATION_MS,
    refetchOnWindowFocus: false,
  });
};
