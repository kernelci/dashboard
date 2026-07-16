import { useCallback, useEffect, useMemo, type JSX } from 'react';

import {
  Link,
  useNavigate,
  useParams,
  useSearch,
} from '@tanstack/react-router';
import { FormattedMessage, useIntl } from 'react-intl';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import PageWithTitle from '@/components/PageWithTitle';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import Tabs from '@/components/Tabs/Tabs';
import type { ITabItem } from '@/components/Tabs/Tabs';

import { useCommits } from '@/api/commitHistory';
import { useTreeCompare } from '@/api/treeCompare';

import {
  compareNavigateFrom,
  compareRouteName,
} from '@/types/tree/TreeCompare';
import type { PossibleTabs } from '@/types/tree/TreeDetails';

import { CompareDeltaTable } from './components/CompareDeltaTable';
import { CompareSummary } from './components/CompareSummary';
import { RevisionSelectorBar } from './components/RevisionSelector';

const SHORT_HASH_LENGTH = 7;

const TreeComparePage = (): JSX.Element => {
  const { formatMessage } = useIntl();
  const { treeName, branch } = useParams({ from: compareRouteName });
  const { hashA, hashB, origin, currentPageTab } = useSearch({
    from: compareRouteName,
  });
  const navigate = useNavigate({ from: compareNavigateFrom });

  const commitsQuery = useCommits({
    origin,
    gitUrl: '',
    gitBranch: branch,
    treeName,
  });

  const revisions = useMemo(
    () =>
      (commitsQuery.data ?? []).map(commit => ({
        hash: commit.git_commit_hash,
        shortHash: commit.git_commit_hash.slice(0, SHORT_HASH_LENGTH),
        commitName: commit.git_commit_name ?? '',
        date: commit.last_checkout ?? commit.earliest_checkout ?? '',
      })),
    [commitsQuery.data],
  );

  const resolvedHashA = hashA || revisions[0]?.hash || '';
  const resolvedHashB =
    hashB ||
    revisions.find(revision => revision.hash !== resolvedHashA)?.hash ||
    '';

  const compareQuery = useTreeCompare({
    treeName,
    branch,
    hashA: resolvedHashA,
    hashB: resolvedHashB,
    origin,
  });

  const updateSearch = useCallback(
    (updates: {
      hashA?: string;
      hashB?: string;
      currentPageTab?: PossibleTabs;
    }) => {
      navigate({
        search: previous => ({
          ...previous,
          hashA: updates.hashA ?? previous.hashA,
          hashB: updates.hashB ?? previous.hashB,
          currentPageTab:
            updates.currentPageTab ??
            previous.currentPageTab ??
            'global.builds',
        }),
        params: { treeName, branch },
      });
    },
    [navigate, treeName, branch],
  );

  useEffect(() => {
    if ((!hashA || !hashB) && resolvedHashA && resolvedHashB) {
      updateSearch({ hashA: resolvedHashA, hashB: resolvedHashB });
    }
  }, [hashA, hashB, resolvedHashA, resolvedHashB, updateSearch]);

  const handleSuggestion = useCallback(
    (suggestion: 'previous' | 'branchHead' | 'swap') => {
      if (suggestion === 'swap') {
        updateSearch({ hashA: resolvedHashB, hashB: resolvedHashA });
        return;
      }

      if (suggestion === 'previous') {
        const currentIndex = revisions.findIndex(r => r.hash === resolvedHashB);
        const previousIndex = Math.min(
          revisions.length - 1,
          Math.max(currentIndex, 0) + 1,
        );
        updateSearch({
          hashA: resolvedHashB,
          hashB: revisions[previousIndex]?.hash ?? resolvedHashA,
        });
        return;
      }

      updateSearch({
        hashA: resolvedHashB,
        hashB: revisions[0]?.hash ?? resolvedHashA,
      });
    },
    [revisions, resolvedHashA, resolvedHashB, updateSearch],
  );

  const tabs: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        content: (
          <CompareDeltaTable
            rows={compareQuery.data?.groups.builds ?? []}
            groupColumnLabelId="treeCompare.group.builds"
          />
        ),
      },
      {
        name: 'global.boots',
        content: (
          <CompareDeltaTable
            rows={compareQuery.data?.groups.boots ?? []}
            groupColumnLabelId="treeCompare.group.boots"
          />
        ),
      },
      {
        name: 'global.tests',
        content: (
          <CompareDeltaTable
            rows={compareQuery.data?.groups.tests ?? []}
            groupColumnLabelId="treeCompare.group.tests"
          />
        ),
      },
    ],
    [compareQuery.data?.groups],
  );

  const pageTitle = formatMessage(
    { id: 'title.treeCompare' },
    { treeName: `${treeName}/${branch}` },
  );

  return (
    <PageWithTitle title={pageTitle}>
      <div className="flex flex-col gap-6 pt-8 pb-8">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink to="/tree" state={s => s}>
                <FormattedMessage id="tree.path" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink
                to="/tree/$treeName/$branch/$hash"
                params={{
                  treeName,
                  branch,
                  hash: resolvedHashA,
                }}
                state={s => s}
              >
                <FormattedMessage id="tree.details" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>
                <FormattedMessage id="treeCompare.breadcrumb" />
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex flex-col gap-2">
          <h1 className="text-dim-black text-2xl font-bold">{pageTitle}</h1>
          <p className="text-dim-gray text-sm">
            <FormattedMessage id="treeCompare.description" />
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div className="text-dim-gray text-sm">
              <span className="text-dim-black font-medium">{treeName}</span>
              <span className="mx-2">·</span>
              <span>{branch}</span>
            </div>
            <Link
              to="/tree/$treeName/$branch/$hash"
              params={{ treeName, branch, hash: resolvedHashA }}
              className="text-blue text-sm font-medium hover:underline"
              state={s => s}
            >
              <FormattedMessage id="treeCompare.backToDetails" />
            </Link>
          </div>
          <QuerySwitcher
            status={commitsQuery.status}
            data={commitsQuery.data}
            error={commitsQuery.error}
          >
            <RevisionSelectorBar
              hashA={resolvedHashA}
              hashB={resolvedHashB}
              revisions={revisions}
              onHashAChange={value => updateSearch({ hashA: value })}
              onHashBChange={value => updateSearch({ hashB: value })}
              onSuggestion={handleSuggestion}
            />
          </QuerySwitcher>
        </div>

        <QuerySwitcher
          status={compareQuery.status}
          data={compareQuery.data}
          error={compareQuery.error}
        >
          {compareQuery.data && (
            <>
              <CompareSummary
                builds={compareQuery.data.summary.builds}
                boots={compareQuery.data.summary.boots}
                tests={compareQuery.data.summary.tests}
              />

              <section>
                <h2 className="text-dim-black mb-4 text-lg font-semibold">
                  <FormattedMessage id="treeCompare.breakdownTitle" />
                </h2>
                <Tabs
                  tabs={tabs}
                  value={currentPageTab}
                  defaultTab="global.builds"
                  onValueChange={value =>
                    updateSearch({ currentPageTab: value as PossibleTabs })
                  }
                />
              </section>
            </>
          )}
        </QuerySwitcher>
      </div>
    </PageWithTitle>
  );
};

export default TreeComparePage;
