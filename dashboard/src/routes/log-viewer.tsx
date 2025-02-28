import { createFileRoute, useSearch } from '@tanstack/react-router';
import type { JSX } from 'react';
import { z } from 'zod';
import pako from 'pako';
import { useQuery } from '@tanstack/react-query';

const logViewerSchema = z.object({
  url: z.string(),
});

async function fetchAndDecompressLog(url: string): Promise<{
  content: string;
  type: 'json' | 'text';
}> {
  // Use our Django backend proxy to avoid CORS issues
  const proxyUrl = `/api/log-proxy?url=${encodeURIComponent(url)}`;

  // Fetch the gzipped file
  const response = await fetch(proxyUrl);
  if (!response.ok) {
    console.log(response);
    throw new Error(`Failed to fetch logs: ${response.statusText}`);
  }

  // Get the file as ArrayBuffer
  const compressedData = await response.arrayBuffer();

  // Decompress using pako
  const decompressedData = pako.inflate(new Uint8Array(compressedData));

  // Convert to string
  const textDecoder = new TextDecoder('utf-8');
  const decompressedText = textDecoder.decode(decompressedData);

  // Determine if JSON or plain text
  const isJson =
    url.endsWith('.json.gz') ||
    (() => {
      try {
        JSON.parse(decompressedText);
        return true;
      } catch (e) {
        return false;
      }
    })();

  return {
    content: decompressedText,
    type: isJson ? 'json' : 'text',
  };
}

function RouteComponent(): JSX.Element {
  const { url } = useSearch({ from: '/log-viewer' });

  const { data, isLoading, error } = useQuery({
    queryKey: ['logs', url],
    queryFn: () => fetchAndDecompressLog(url),
    enabled: !!url,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });

  const renderLogContent = () => {
    if (isLoading) {
      return <div>Loading logs...</div>;
    }
    if (error) {
      return (
        <div className="error">
          Error:{' '}
          {error instanceof Error ? error.message : 'Failed to load logs'}
        </div>
      );
    }
    if (!data) {
      return <div>No log content available</div>;
    }

    if (data.type === 'json') {
      try {
        const jsonData = JSON.parse(data.content);
        return (
          <pre className="json-logs">{JSON.stringify(jsonData, null, 2)}</pre>
        );
      } catch (e) {
        return <div>Error parsing JSON: {String(e)}</div>;
      }
    } else {
      return <pre className="text-logs">{data.content}</pre>;
    }
  };

  return (
    <div className="log-viewer">
      <h3>Log Viewer: {url}</h3>
      {data?.type && (
        <div className="log-type">
          Format: {data.type === 'json' ? 'JSON' : 'Plain text'}
        </div>
      )}
      <div className="log-content">{renderLogContent()}</div>
    </div>
  );
}

export const Route = createFileRoute('/log-viewer')({
  validateSearch: logViewerSchema,
  component: RouteComponent,
});
