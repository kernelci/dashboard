import { useRouterState, useSearch } from '@tanstack/react-router';
import { useMemo, type JSX } from 'react';

const Constants = {
  URL_DOMAIN_SIZE: 90,
  URL_END_PATH_SIZE: 50,
} as const;

import { FormattedMessage } from 'react-intl';

import { LogExcerpt } from '@/components/Log/LogExcerpt';
import { truncateUrl } from '@/lib/string';
import { useLogViewer } from '@/api/logViewer';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { useLogData } from '@/hooks/useLogData';
import { LogViewerCard } from '@/components/Log/LogViewerCard';
import {
  type BreadcrumbRoute,
  MemoizedBreadcrumbGenerator,
  type IBreadcrumbComponent,
} from '@/components/Breadcrumb/BreadcrumbGenerator';
import { useSearchStore } from '@/hooks/store/useSearchStore';

const routes: BreadcrumbRoute = {
  tree: {
    base: { path: '/tree', messageId: 'tree.path' },
    details: {
      path: '/tree/$treeId',
      paramKey: 'treeId',
      messageId: 'tree.details',
    },
    build: {
      path: '/tree/$treeId/build/$buildId',
      messageId: 'buildDetails.buildDetails',
    },
    test: { path: '/tree/$treeId/test/$testId', messageId: 'test.details' },
  },
  hardware: {
    base: { path: '/hardware', messageId: 'hardware.path' },
    details: {
      path: '/hardware/$hardwareId',
      paramKey: 'hardwareId',
      messageId: 'hardware.details',
    },
    build: {
      path: '/hardware/$hardwareId/build/$buildId',
      messageId: 'buildDetails.buildDetails',
    },
    test: {
      path: '/hardware/$hardwareId/test/$testId',
      messageId: 'test.details',
    },
  },
};

export function LogViewer(): JSX.Element {
  const { url, type, itemId } = useSearch({ from: '/log-viewer' });
  const historyState = useRouterState({ select: s => s.location.state });
  const previousSearch = useSearchStore(s => s.previousSearch);

  const { data, status } = useLogViewer(url);
  const { data: logData, isLoading } = useLogData(itemId ?? '', type);

  const breadcrumbComponent = useMemo(() => {
    if (!type || !itemId) {
      return undefined;
    }

    if (type !== 'build' && type !== 'test') {
      return undefined;
    }

    const components: IBreadcrumbComponent[] = [];

    const historyFrom = historyState.from as keyof typeof routes;
    if (historyState.id !== undefined && routes[historyFrom]) {
      const { base, details, build, test } = routes[historyFrom];

      components.push({
        linkProps: { to: base.path, search: s => ({ origin: s.origin }) },
        messageId: base.messageId,
      });

      components.push({
        linkProps: {
          to: details.path,
          params: { [details.paramKey]: historyState.id },
          state: s => s,
          search: previousSearch,
        },
        messageId: details.messageId,
      });

      if (type === 'build') {
        components.push({
          linkProps: {
            to: build.path,
            params: { [details.paramKey]: historyState.id, buildId: itemId },
          },
          messageId: build.messageId,
        });
      } else {
        components.push({
          linkProps: {
            to: test.path,
            params: { [details.paramKey]: historyState.id, buildId: itemId },
          },
          messageId: test.messageId,
        });
      }
    } else {
      if (type === 'build') {
        components.push({
          linkProps: {
            to: '/build/$buildId',
            params: { buildId: itemId },
          },
          messageId: 'buildDetails.buildDetails',
        });
      } else if (type === 'test') {
        components.push({
          linkProps: {
            to: '/test/$testId',
            params: { buildId: itemId },
          },
          messageId: 'test.details',
        });
      }
    }

    components.push({ linkProps: {}, messageId: 'logSheet.title' });

    return <MemoizedBreadcrumbGenerator components={components} />;
  }, [type, itemId, historyState, previousSearch]);

  return (
    <main className="bg-light-gray min-h-[100vh] border-2 px-8 pt-14 pb-3">
      <div className="mb-3 px-3">
        <h1 className="mb-3 text-4xl font-medium">
          <FormattedMessage id="logSheet.title" />
        </h1>
        {breadcrumbComponent}
        <div className="px-0">
          {logData.log_excerpt && (
            <LogViewerCard
              logData={logData}
              isLoading={isLoading}
              variant="full"
            />
          )}
          <p className="text-xl">
            <FormattedMessage id="logViewer.download" />
          </p>
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="hover:text-blue text-dark-blue underline transition"
          >
            {truncateUrl(
              url,
              Constants.URL_DOMAIN_SIZE,
              Constants.URL_END_PATH_SIZE,
            )}
          </a>
        </div>
      </div>
      <div className="overflow-hidden rounded-md">
        <QuerySwitcher data={data} status={status}>
          <LogExcerpt logExcerpt={data?.content} variant="log-viewer" />
        </QuerySwitcher>
      </div>
    </main>
  );
}
