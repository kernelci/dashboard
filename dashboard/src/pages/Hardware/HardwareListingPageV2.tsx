import { useEffect, useMemo, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { Toaster } from '@/components/ui/toaster';

import type { HardwareItem, HardwareRevisionSelection } from '@/types/hardware';

import {
  useHardwareListingByRevision,
  useHardwareSelectors,
} from '@/api/hardware';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';

import {
  includesInAnStringOrStringArray,
  matchesRegexOrIncludes,
} from '@/lib/string';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';
import type { SearchIntent } from '@/lib/intent';

import { HardwareTable } from './HardwareTable';
import {
  decodeBranchValue,
  findSelectionByCommitTokens,
  getBranchBySelection,
  getSelectionForBranchChange,
  getSelectionForTreeChange,
  getTreeBySelection,
  resolveHardwareSelection,
  type HardwareRevisionSelectorValue,
} from './hardwareSelection';

interface HardwareListingPageV2Props {
  intent: SearchIntent;
  urlFromMap: HardwareListingRoutesMap['v2'];
}

const HardwareListingPageV2 = ({
  intent,
  urlFromMap,
}: HardwareListingPageV2Props): JSX.Element => {
  const navigate = useNavigate({ from: urlFromMap.navigate });
  const { origin, treeName, gitRepositoryUrl, gitBranch, gitCommitHash } =
    useSearch({ from: urlFromMap.search });
  const inputFilter = intent.search;
  const intentCommits =
    intent.intent === 'commits' ? intent.commits : undefined;

  const {
    data: selectorsData,
    error: selectorsError,
    status: selectorsStatus,
  } = useHardwareSelectors(urlFromMap.search);
  const selectors = useMemo(() => selectorsData?.trees ?? [], [selectorsData]);

  const hasSelectionParams = Boolean(
    treeName || gitRepositoryUrl || gitBranch || gitCommitHash,
  );

  const resolvedSelection = useMemo(() => {
    const selectionFromUrl =
      treeName && gitRepositoryUrl && gitBranch && gitCommitHash
        ? {
            treeName,
            gitRepositoryUrl,
            gitBranch,
            gitCommitHash,
          }
        : null;

    return resolveHardwareSelection({
      trees: selectors,
      selectionFromUrl,
      hasSelectionParams,
      intentCommits,
    });
  }, [
    selectors,
    treeName,
    gitRepositoryUrl,
    gitBranch,
    gitCommitHash,
    hasSelectionParams,
    intentCommits,
  ]);

  const intentMatchedSelection = useMemo(() => {
    if (!intentCommits) {
      return null;
    }

    return (
      findSelectionByCommitTokens(selectors, intentCommits)?.selection ?? null
    );
  }, [selectors, intentCommits]);

  useEffect(() => {
    if (!intentCommits || selectorsStatus !== 'success') {
      return;
    }

    if (intentMatchedSelection === null) {
      return;
    }

    navigate({
      search: previousSearch => ({
        ...previousSearch,
        treeName: intentMatchedSelection.treeName,
        gitRepositoryUrl: intentMatchedSelection.gitRepositoryUrl,
        gitBranch: intentMatchedSelection.gitBranch,
        gitCommitHash: intentMatchedSelection.gitCommitHash,
      }),
      state: s => s,
      replace: true,
    });
  }, [
    hasSelectionParams,
    intentCommits,
    intentMatchedSelection,
    navigate,
    selectorsStatus,
  ]);

  const {
    data: listingData,
    error: listingError,
    status: listingStatus,
    isLoading: isListingLoading,
  } = useHardwareListingByRevision(
    resolvedSelection.selection,
    urlFromMap.search,
  );

  const selectedTree = useMemo(() => {
    if (resolvedSelection.selection === null) {
      return null;
    }

    return getTreeBySelection(selectors, resolvedSelection.selection.treeName);
  }, [selectors, resolvedSelection.selection]);

  const selectedBranch = useMemo(() => {
    if (resolvedSelection.selection === null || selectedTree === null) {
      return null;
    }

    return getBranchBySelection(
      selectedTree,
      resolvedSelection.selection.gitRepositoryUrl,
      resolvedSelection.selection.gitBranch,
    );
  }, [resolvedSelection.selection, selectedTree]);

  const listItems: HardwareItem[] = useMemo(() => {
    if (!listingData || listingError) {
      return [];
    }

    const currentData = listingData.hardware;

    return currentData
      .filter(hardware => {
        return (
          matchesRegexOrIncludes(hardware.platform, inputFilter) ||
          includesInAnStringOrStringArray(hardware.hardware ?? '', inputFilter)
        );
      })
      .sort((a, b) => a.platform.localeCompare(b.platform));
  }, [listingData, listingError, inputFilter]);

  const revisionStartTimestampInSeconds = resolvedSelection.revisionStartTime
    ? dateObjectToTimestampInSeconds(
        new Date(resolvedSelection.revisionStartTime),
      )
    : 0;

  const revisionEndTimestampInSeconds = revisionStartTimestampInSeconds
    ? revisionStartTimestampInSeconds + daysToSeconds(REDUCED_TIME_SEARCH)
    : 0;

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="hardwareListing"
        args={{ cmdName: 'hardware list', origin: origin, json: true }}
      />
    ),
    [origin],
  );

  const navigateToSelection = (
    nextSelection: HardwareRevisionSelection,
  ): void => {
    navigate({
      search: previousSearch => ({
        ...previousSearch,
        treeName: nextSelection.treeName,
        gitRepositoryUrl: nextSelection.gitRepositoryUrl,
        gitBranch: nextSelection.gitBranch,
        gitCommitHash: nextSelection.gitCommitHash,
        hardwareSearch: '',
      }),
      state: s => s,
    });
  };

  const onTreeChange = ({
    tree,
    branch,
    revision,
  }: HardwareRevisionSelectorValue): void => {
    if (!tree) {
      return;
    }

    if (branch) {
      const selectedTreeByName = getTreeBySelection(selectors, tree);
      if (selectedTreeByName === null) {
        return;
      }

      const branchSelection = decodeBranchValue(branch);
      if (branchSelection === null) {
        return;
      }

      if (revision) {
        navigateToSelection({
          treeName: tree,
          gitRepositoryUrl: branchSelection.gitRepositoryUrl,
          gitBranch: branchSelection.gitBranch,
          gitCommitHash: revision,
        });
        return;
      }

      const nextSelection = getSelectionForBranchChange({
        tree: selectedTreeByName,
        gitRepositoryUrl: branchSelection.gitRepositoryUrl,
        gitBranch: branchSelection.gitBranch,
      });
      if (nextSelection === null) {
        return;
      }

      navigateToSelection(nextSelection);
      return;
    }

    const nextSelection = getSelectionForTreeChange({
      trees: selectors,
      treeName: tree,
    });
    if (nextSelection === null) {
      return;
    }

    navigateToSelection(nextSelection);
  };

  const hasSelectors = selectors.length > 0;
  const hasListingRows = Boolean((listingData?.hardware.length ?? 0) > 0);
  const tableEmptyMessageId =
    !hasListingRows && inputFilter.length === 0
      ? 'hardwareListing.revisionEmpty'
      : 'hardwareListing.notFound';

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6">
        {selectorsStatus === 'error' && (
          <div className="w-full py-6 text-center">
            <span className="text-weak-gray text-sm">
              {selectorsError?.message}
            </span>
          </div>
        )}

        {selectorsStatus === 'pending' && (
          <div className="w-full py-6 text-center">
            <FormattedMessage id="global.loading" />
          </div>
        )}

        {selectorsStatus === 'success' && (
          <>
            {!hasSelectors && (
              <div className="text-weak-gray flex flex-col items-center py-10 text-center text-lg font-semibold">
                <FormattedMessage id="hardwareListing.selectorsNoData" />
              </div>
            )}

            {hasSelectors && (
              <>
                <span className="text-dim-gray flex-1 justify-start text-left text-sm">
                  <FormattedMessage
                    id="global.projectUnderDevelopment"
                    values={{ br: <br /> }}
                  />
                </span>

                <HardwareTable
                  treeTableRows={listItems}
                  endTimestampInSeconds={revisionEndTimestampInSeconds}
                  startTimestampInSeconds={revisionStartTimestampInSeconds}
                  status={listingStatus}
                  queryData={listingData}
                  error={listingError}
                  isLoading={isListingLoading}
                  navigateFrom={urlFromMap.navigate}
                  emptyMessageId={tableEmptyMessageId}
                  selectors={selectors}
                  selectedTree={selectedTree}
                  selectedBranch={selectedBranch}
                  selection={resolvedSelection.selection}
                  onTreeChange={onTreeChange}
                />
              </>
            )}
          </>
        )}
      </div>
      {kcidevComponent}
    </>
  );
};

export default HardwareListingPageV2;
