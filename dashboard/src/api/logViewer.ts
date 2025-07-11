import pako from 'pako';
import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { minutesToMilliseconds } from 'date-fns';

import { RequestData } from './commonRequest';

import { LOG_EXCERPT_ALLOWED_DOMAINS } from '@/utils/constants/log_excerpt_allowed_domain';

// eslint-disable-next-line no-magic-numbers
const STALE_DURATION_MS = minutesToMilliseconds(60);

type FetchAndDecompressLogsResponse = {
  content: string;
};
async function fetchAndDecompressLog(
  url: string,
): Promise<FetchAndDecompressLogsResponse> {
  const proxyUrl = `/api/proxy/?url=${encodeURIComponent(url)}`;
  const urlPathname = new URL(url).pathname;
  const isGzipped = urlPathname.endsWith('.gz');

  try {
    if (isGzipped) {
      const response = await RequestData.get<ArrayBuffer>(proxyUrl, {
        responseType: 'arraybuffer',
      });

      const uint8ArrayResponse = new Uint8Array(response);
      const decompressedData = pako.inflate(uint8ArrayResponse);
      const textDecoder = new TextDecoder('utf-8');
      const decompressedText = textDecoder.decode(decompressedData);

      return { content: decompressedText };
    } else {
      // For non-gzipped files, request as text
      const response = await RequestData.get<string>(proxyUrl, {
        responseType: 'text',
      });

      return { content: response };
    }
  } catch (error) {
    console.error(error);
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

function isAllowedUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return LOG_EXCERPT_ALLOWED_DOMAINS.includes(url.hostname);
  } catch {
    return false;
  }
}

export const useLogExcerptUrl = (logExcerpt: string) => {
  const isLogExcerptFetchable = isAllowedUrl(logExcerpt);

  const { data: logExcerptData, status: logExcerptStatus } =
    isLogExcerptFetchable
      ? useLogViewer(logExcerpt)
      : { data: { content: logExcerpt }, status: 'success' as 'success' } as const;

  return { data: logExcerptData, status: logExcerptStatus } as const;
};
