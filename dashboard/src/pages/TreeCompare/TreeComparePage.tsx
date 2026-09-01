import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';

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
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import PageWithTitle from '@/components/PageWithTitle';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import Tabs from '@/components/Tabs/Tabs';
import type { ITabItem } from '@/components/Tabs/Tabs';

import { useCommits } from '@/api/commitHistory';
import {
  useTreeCompare,
  useTreeCompareBoots,
  useTreeCompareBuilds,
  useTreeCompareTests,
} from '@/api/treeCompare';

import {
  compareDefaultChangeFilters,
  compareNavigateFrom,
  compareRouteName,
  type CompareBootFailureRow,
  type CompareChangeFilter,
  type CompareTestFailureRow,
} from '@/types/tree/TreeCompare';
import type { PossibleTabs } from '@/types/tree/TreeDetails';
import {
  applyChangeFilter,
  mapBootOrTestDiffRows,
  mapBuildDiffRows,
} from '@/utils/treeCompareDiff';

import { CompareChangeFilterBar } from './components/CompareChangeStats';
import {
  CompareDetailSheet,
  compareRowToDetailItem,
} from './components/CompareDetailSheet';
import {
  CompareBootsFailuresTable,
  CompareBuildsFailuresTable,
  CompareTestsFailuresTable,
} from './components/CompareFailuresTables';
import { CompareSummary } from './components/CompareSummary';
import { RevisionSelectorBar } from './components/RevisionSelector';

const SHORT_HASH_LENGTH = 7;

const TreeComparePage = (): JSX.Element => {
  const { formatMessage } = useIntl();
  const { treeName, branch } = useParams({ from: compareRouteName });
  const { hashA, hashB, origin, currentPageTab, changeFilter } = useSearch({
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
        tags: commit.git_commit_tags ?? [],
      })),
    [commitsQuery.data],
  );

  const resolvedHashA = hashA || revisions[0]?.hash || '';
  const resolvedHashB =
    hashB ||
    revisions.find(revision => revision.hash !== resolvedHashA)?.hash ||
    '';

  const canCompare = Boolean(resolvedHashA && resolvedHashB);

  const compareParams = {
    treeName,
    branch,
    hashA: resolvedHashA,
    hashB: resolvedHashB,
    origin,
  };

  const compareQuery = useTreeCompare(compareParams);
  const buildsDiffQuery = useTreeCompareBuilds(compareParams);
  const bootsDiffQuery = useTreeCompareBoots(compareParams);
  const testsDiffQuery = useTreeCompareTests(compareParams);

  const updateSearch = useCallback(
    (updates: {
      hashA?: string;
      hashB?: string;
      currentPageTab?: PossibleTabs;
      changeFilter?: CompareChangeFilter[];
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
          changeFilter:
            updates.changeFilter ??
            previous.changeFilter ??
            compareDefaultChangeFilters,
        }),
        params: { treeName, branch },
        resetScroll: false,
      });
    },
    [navigate, treeName, branch],
  );

  useEffect(() => {
    if ((!hashA || !hashB) && resolvedHashA && resolvedHashB) {
      updateSearch({ hashA: resolvedHashA, hashB: resolvedHashB });
    }
  }, [hashA, hashB, resolvedHashA, resolvedHashB, updateSearch]);

  const handleSwap = useCallback(() => {
    updateSearch({ hashA: resolvedHashB, hashB: resolvedHashA });
  }, [resolvedHashA, resolvedHashB, updateSearch]);

  const handleSideAction = useCallback(
    (side: 'A' | 'B', action: 'previous' | 'branchHead') => {
      const currentHash = side === 'A' ? resolvedHashA : resolvedHashB;
      const currentIndex = revisions.findIndex(r => r.hash === currentHash);

      if (action === 'previous') {
        const previousIndex = Math.min(
          revisions.length - 1,
          Math.max(currentIndex, 0) + 1,
        );
        const nextHash = revisions[previousIndex]?.hash ?? currentHash;
        if (side === 'A') {
          updateSearch({ hashA: nextHash });
        } else {
          updateSearch({ hashB: nextHash });
        }
        return;
      }

      const headHash = revisions[0]?.hash ?? currentHash;
      if (side === 'A') {
        updateSearch({ hashA: headHash });
      } else {
        updateSearch({ hashB: headHash });
      }
    },
    [revisions, resolvedHashA, resolvedHashB, updateSearch],
  );

  const buildRows = useMemo(
    () => mapBuildDiffRows(buildsDiffQuery.data ?? []),
    [buildsDiffQuery.data],
  );
  const bootRows = useMemo(
    () =>
      mapBootOrTestDiffRows(
        bootsDiffQuery.data ?? [],
        'boot',
      ) as CompareBootFailureRow[],
    [bootsDiffQuery.data],
  );
  const testRows = useMemo(
    () =>
      mapBootOrTestDiffRows(
        testsDiffQuery.data ?? [],
        'test',
      ) as CompareTestFailureRow[],
    [testsDiffQuery.data],
  );

  const filteredBuilds = useMemo(
    () => applyChangeFilter(buildRows, changeFilter),
    [buildRows, changeFilter],
  );
  const filteredBoots = useMemo(
    () => applyChangeFilter(bootRows, changeFilter),
    [bootRows, changeFilter],
  );
  const filteredTests = useMemo(
    () => applyChangeFilter(testRows, changeFilter),
    [changeFilter, testRows],
  );

  const [selectedId, setSelectedId] = useState<string | null>(null);

  const visibleRows = useMemo(() => {
    if (currentPageTab === 'global.boots') {
      return filteredBoots;
    }
    if (currentPageTab === 'global.tests') {
      return filteredTests;
    }
    return filteredBuilds;
  }, [currentPageTab, filteredBoots, filteredBuilds, filteredTests]);

  const selectedIndex = visibleRows.findIndex(row => row.id === selectedId);
  const selectedRow = selectedIndex >= 0 ? visibleRows[selectedIndex] : null;
  const logType = currentPageTab === 'global.builds' ? 'build' : 'test';

  const openRow = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  const closeSheet = useCallback((open: boolean) => {
    if (!open) {
      setSelectedId(null);
    }
  }, []);

  const goToPrevious = useCallback(() => {
    if (selectedIndex > 0) {
      setSelectedId(visibleRows[selectedIndex - 1]?.id ?? null);
    }
  }, [selectedIndex, visibleRows]);

  const goToNext = useCallback(() => {
    if (selectedIndex >= 0 && selectedIndex < visibleRows.length - 1) {
      setSelectedId(visibleRows[selectedIndex + 1]?.id ?? null);
    }
  }, [selectedIndex, visibleRows]);

  const tabs: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        rightElement: (
          <ColoredCircle
            quantity={filteredBuilds.length}
            backgroundClassName="bg-light-red"
          />
        ),
        content: (
          <QuerySwitcher
            status={buildsDiffQuery.status}
            data={buildsDiffQuery.data}
            error={buildsDiffQuery.error}
          >
            <CompareBuildsFailuresTable
              rows={filteredBuilds}
              selectedId={selectedId}
              onRowClick={openRow}
            />
          </QuerySwitcher>
        ),
      },
      {
        name: 'global.boots',
        rightElement: (
          <ColoredCircle
            quantity={filteredBoots.length}
            backgroundClassName="bg-light-red"
          />
        ),
        content: (
          <QuerySwitcher
            status={bootsDiffQuery.status}
            data={bootsDiffQuery.data}
            error={bootsDiffQuery.error}
          >
            <CompareBootsFailuresTable
              rows={filteredBoots}
              selectedId={selectedId}
              onRowClick={openRow}
            />
          </QuerySwitcher>
        ),
      },
      {
        name: 'global.tests',
        rightElement: (
          <ColoredCircle
            quantity={filteredTests.length}
            backgroundClassName="bg-light-red"
          />
        ),
        content: (
          <QuerySwitcher
            status={testsDiffQuery.status}
            data={testsDiffQuery.data}
            error={testsDiffQuery.error}
          >
            <CompareTestsFailuresTable
              rows={filteredTests}
              selectedId={selectedId}
              onRowClick={openRow}
            />
          </QuerySwitcher>
        ),
      },
    ],
    [
      bootsDiffQuery.data,
      bootsDiffQuery.error,
      bootsDiffQuery.status,
      buildsDiffQuery.data,
      buildsDiffQuery.error,
      buildsDiffQuery.status,
      filteredBoots,
      filteredBuilds,
      filteredTests,
      openRow,
      selectedId,
      testsDiffQuery.data,
      testsDiffQuery.error,
      testsDiffQuery.status,
    ],
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
              onSideAction={handleSideAction}
              onSwap={handleSwap}
            />
          </QuerySwitcher>
        </div>

        {!canCompare && commitsQuery.status === 'success' && (
          <div className="text-dim-gray rounded-lg border border-gray-200 bg-white px-4 py-6 text-sm">
            <FormattedMessage id="treeCompare.needTwoRevisions" />
          </div>
        )}

        {canCompare && (
          <>
            <QuerySwitcher
              status={compareQuery.status}
              data={compareQuery.data}
              error={compareQuery.error}
            >
              {compareQuery.data && (
                <CompareSummary
                  builds={compareQuery.data.summary.builds}
                  boots={compareQuery.data.summary.boots}
                  tests={compareQuery.data.summary.tests}
                />
              )}
            </QuerySwitcher>

            <section>
              <h2 className="text-dim-black mb-4 text-lg font-semibold">
                <FormattedMessage id="treeCompare.breakdownTitle" />
              </h2>
              <div className="bg-light-blue text-dark-blue mb-4 flex items-start gap-2 rounded-lg px-3 py-2.5 text-sm">
                <FormattedMessage id="treeCompare.drilldownHint" />
              </div>
              <div className="mb-4">
                <CompareChangeFilterBar
                  value={changeFilter}
                  onChange={value => updateSearch({ changeFilter: value })}
                />
              </div>
              <Tabs
                tabs={tabs}
                value={currentPageTab}
                defaultTab="global.builds"
                onValueChange={value =>
                  updateSearch({ currentPageTab: value as PossibleTabs })
                }
              />
            </section>
            <CompareDetailSheet
              open={selectedRow !== null}
              item={selectedRow ? compareRowToDetailItem(selectedRow) : null}
              logType={logType}
              onOpenChange={closeSheet}
              onPrevious={goToPrevious}
              onNext={goToNext}
              hasPrevious={selectedIndex > 0}
              hasNext={
                selectedIndex >= 0 && selectedIndex < visibleRows.length - 1
              }
            />
          </>
        )}
      </div>
    </PageWithTitle>
  );
};

export default TreeComparePage;
