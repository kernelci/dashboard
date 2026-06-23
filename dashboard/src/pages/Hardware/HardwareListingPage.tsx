import { useCallback, useEffect, useMemo, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';
import { roundToNearestMinutes } from 'date-fns';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { Toaster } from '@/components/ui/toaster';

import type { HardwareItem, HardwareRevisionSelection } from '@/types/hardware';

import {
  useHardwareListing,
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
  type HardwareRevisionSelectorValue,
} from './hardwareSelection';

interface HardwareListingPageProps {
  intent: SearchIntent;
  urlFromMap: HardwareListingRoutesMap;
}

const HardwareListingPage = ({
  intent,
  urlFromMap,
}: HardwareListingPageProps): JSX.Element => {
  const navigate = useNavigate({ from: urlFromMap.navigate });
  const {
    origin,
    intervalInDays,
    treeName,
    gitRepositoryUrl,
    gitBranch,
    gitCommitHash,
  } = useSearch({ from: urlFromMap.search });
  const inputFilter = intent.search;
  const intentCommits =
    intent.intent === 'commits' ? intent.commits : undefined;

  const { startTimestampInSeconds, endTimestampInSeconds } = useMemo(() => {
    const end = dateObjectToTimestampInSeconds(
      roundToNearestMinutes(new Date(), { nearestTo: 30 }),
    );
    return {
      startTimestampInSeconds: end - daysToSeconds(intervalInDays),
      endTimestampInSeconds: end,
    };
  }, [intervalInDays]);

  const selection: HardwareRevisionSelection | null = useMemo(() => {
    if (treeName && gitRepositoryUrl && gitBranch && gitCommitHash) {
      return { treeName, gitRepositoryUrl, gitBranch, gitCommitHash };
    }
    return null;
  }, [treeName, gitRepositoryUrl, gitBranch, gitCommitHash]);
  const hasSelection = selection !== null;
  const hasSelectionParams = Boolean(
    treeName || gitRepositoryUrl || gitBranch || gitCommitHash,
  );

  const { data: selectorsData, status: selectorsStatus } = useHardwareSelectors(
    urlFromMap.search,
  );

  const trees = useMemo(() => selectorsData?.trees ?? [], [selectorsData]);

  const intentMatchedSelection = useMemo(() => {
    if (!intentCommits) {
      return null;
    }

    return findSelectionByCommitTokens(trees, intentCommits)?.selection ?? null;
  }, [trees, intentCommits]);

  const navigateToSelection = useCallback(
    (
      nextSelection: HardwareRevisionSelection,
      options?: { replace?: boolean; clearHardwareSearch?: boolean },
    ): void => {
      const clearHardwareSearch = options?.clearHardwareSearch ?? true;

      navigate({
        search: previousSearch => ({
          ...previousSearch,
          treeName: nextSelection.treeName,
          gitRepositoryUrl: nextSelection.gitRepositoryUrl,
          gitBranch: nextSelection.gitBranch,
          gitCommitHash: nextSelection.gitCommitHash,
          ...(clearHardwareSearch ? { hardwareSearch: '' } : {}),
        }),
        state: s => s,
        replace: options?.replace,
      });
    },
    [navigate],
  );

  useEffect(() => {
    if (
      !intentCommits ||
      selectorsStatus !== 'success' ||
      hasSelectionParams ||
      intentMatchedSelection === null
    ) {
      return;
    }

    navigateToSelection(intentMatchedSelection, {
      replace: true,
      clearHardwareSearch: false,
    });
  }, [
    hasSelectionParams,
    intentCommits,
    intentMatchedSelection,
    navigateToSelection,
    selectorsStatus,
  ]);

  const selectedTree = useMemo(() => {
    if (!treeName) {
      return null;
    }

    return getTreeBySelection(trees, treeName);
  }, [trees, treeName]);

  const selectedBranch = useMemo(() => {
    if (selectedTree === null || !gitRepositoryUrl || !gitBranch) {
      return null;
    }

    return getBranchBySelection(selectedTree, gitRepositoryUrl, gitBranch);
  }, [selectedTree, gitRepositoryUrl, gitBranch]);

  const defaultListing = useHardwareListing(
    startTimestampInSeconds,
    endTimestampInSeconds,
    urlFromMap.search,
    intentCommits,
    !hasSelection,
  );
  const revisionListing = useHardwareListingByRevision(
    selection,
    urlFromMap.search,
  );
  const activeListing = hasSelection ? revisionListing : defaultListing;

  const listItems: HardwareItem[] = useMemo(() => {
    const listingData = activeListing.data;
    if (!listingData || activeListing.error) {
      return [];
    }

    return listingData.hardware
      .filter(hardware => {
        return (
          matchesRegexOrIncludes(hardware.platform, inputFilter) ||
          includesInAnStringOrStringArray(hardware.hardware ?? '', inputFilter)
        );
      })
      .map((hardware): HardwareItem => {
        return {
          hardware: hardware.hardware,
          platform: hardware.platform,
          build_status_summary: hardware.build_status_summary,
          test_status_summary: hardware.test_status_summary,
          boot_status_summary: hardware.boot_status_summary,
        };
      })
      .sort((a, b) => a.platform.localeCompare(b.platform));
  }, [activeListing.data, activeListing.error, inputFilter]);

  const selectedRevision =
    hasSelection && gitCommitHash
      ? selectedBranch?.revisions.find(
          revision => revision.git_commit_hash === gitCommitHash,
        )
      : undefined;
  const revisionStartTimestampInSeconds = selectedRevision
    ? dateObjectToTimestampInSeconds(new Date(selectedRevision.start_time))
    : 0;
  const revisionEndTimestampInSeconds = revisionStartTimestampInSeconds
    ? revisionStartTimestampInSeconds + daysToSeconds(REDUCED_TIME_SEARCH)
    : 0;

  const tableStartTimestampInSeconds = hasSelection
    ? revisionStartTimestampInSeconds
    : startTimestampInSeconds;
  const tableEndTimestampInSeconds = hasSelection
    ? revisionEndTimestampInSeconds
    : endTimestampInSeconds;

  const kcidevComponent = useMemo(
    () => (
      <MemoizedKcidevFooter
        commandGroup="hardwareListing"
        args={{ cmdName: 'hardware list', origin: origin, json: true }}
      />
    ),
    [origin],
  );

  const onTreeChange = ({
    tree,
    branch,
    revision,
  }: HardwareRevisionSelectorValue): void => {
    if (!tree) {
      return;
    }

    if (branch) {
      const selectedTreeByName = getTreeBySelection(trees, tree);
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
      trees,
      treeName: tree,
    });
    if (nextSelection === null) {
      return;
    }

    navigateToSelection(nextSelection);
  };

  const onClearSelection = (): void => {
    navigate({
      search: previousSearch => ({
        ...previousSearch,
        treeName: undefined,
        gitRepositoryUrl: undefined,
        gitBranch: undefined,
        gitCommitHash: undefined,
      }),
      state: s => s,
    });
  };

  const hasListingRows = Boolean(
    (activeListing.data?.hardware.length ?? 0) > 0,
  );
  const tableEmptyMessageId =
    hasSelection && !hasListingRows && inputFilter.length === 0
      ? 'hardwareListing.revisionEmpty'
      : 'hardwareListing.notFound';

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6">
        <span className="text-dim-gray flex-1 justify-start text-left text-sm">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={{ br: <br /> }}
          />
        </span>

        <HardwareTable
          treeTableRows={listItems}
          endTimestampInSeconds={tableEndTimestampInSeconds}
          startTimestampInSeconds={tableStartTimestampInSeconds}
          status={activeListing.status}
          queryData={activeListing.data}
          error={activeListing.error}
          isLoading={activeListing.isLoading}
          navigateFrom={urlFromMap.navigate}
          emptyMessageId={tableEmptyMessageId}
          selectors={trees}
          selectedTree={selectedTree}
          selectedBranch={selectedBranch}
          selection={selection}
          selectorsLoading={selectorsStatus === 'pending'}
          onTreeChange={onTreeChange}
          onClearSelection={onClearSelection}
        />
      </div>
      {kcidevComponent}
    </>
  );
};

export default HardwareListingPage;
