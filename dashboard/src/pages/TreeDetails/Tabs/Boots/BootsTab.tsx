import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import BaseCard from '@/components/Cards/BaseCard';
import { Skeleton } from '@/components/Skeleton';

import { BootsTable } from '@/components/BootsTable/BootsTable';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import MemoizedHardwareTested from '@/components/Cards/HardwareTested';
import {
  zTableFilterInfoDefault,
  type TestsTableFilter,
} from '@/types/tree/TreeDetails';
import {
  DesktopGrid,
  MobileGrid,
  InnerMobileGrid,
} from '@/components/Tabs/TabGrid';

import MemoizedConfigList from '@/components/Tabs/Tests/ConfigsList';

import MemoizedErrorsSummary from '@/components/Tabs/Tests/ErrorsSummary';

import MemoizedStatusCard from '@/components/Tabs/Tests/StatusCard';
import { RedirectFrom } from '@/types/general';

import TreeCommitNavigationGraph from '@/pages/TreeDetails/Tabs/TreeCommitNavigationGraph';
import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

interface BootsTabProps {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
}

const BootsTab = ({ treeDetailsLazyLoaded }: BootsTabProps): JSX.Element => {
  const { treeId } = useParams({
    from: '/tree/$treeId',
  });

  const searchParams = useSearch({
    from: '/tree/$treeId',
  });

  const { tableFilter, diffFilter } = searchParams;
  const currentPathFilter = diffFilter.bootPath
    ? Object.keys(diffFilter.bootPath)[0]
    : undefined;

  const navigate = useNavigate({ from: '/tree/$treeId' });

  const updatePathFilter = useCallback(
    (pathFilter: string) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          diffFilter: {
            ...previousSearch.diffFilter,
            bootPath: pathFilter === '' ? undefined : { [pathFilter]: true },
          },
        }),
        state: s => s,
      });
    },
    [navigate],
  );

  const onClickFilter = useCallback(
    (newFilter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              bootsTable: newFilter,
            },
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const { isLoading, data, error } = treeDetailsLazyLoaded.summary;
  const { data: fullData, status: fullStatus } = treeDetailsLazyLoaded.full;

  const bootsData = fullData?.boots;

  const getRowLink = useCallback(
    (bootId: string): LinkProps => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: bootId,
        treeId: treeId,
      },
      search: s => s,
    }),
    [treeId],
  );

  const hardwareData = useMemo(() => {
    return {
      ...data?.summary.boots.environment_compatible,
      ...data?.summary.boots.environment_misc,
    };
  }, [
    data?.summary.boots.environment_compatible,
    data?.summary.boots.environment_misc,
  ]);

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.error" />
      </div>
    );
  }

  if (isLoading)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  if (!data) return <div />;

  if (bootsData?.length === 0) {
    return (
      <BaseCard
        title={<FormattedMessage id="bootsTab.info" />}
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
            <FormattedMessage id="bootsTab.info.description" />
          </p>
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            title={<FormattedMessage id="bootsTab.bootStatus" />}
            statusCounts={data.summary.boots.status}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={data.summary.boots.configs}
            diffFilter={diffFilter}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.summary.boots.architectures}
            diffFilter={diffFilter}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={data.summary.boots.issues}
            failedWithUnknownIssues={data.summary.boots.unknown_issues}
            diffFilter={diffFilter}
            issueFilterSection="bootIssue"
            detailsId={treeId}
            pageFrom={RedirectFrom.Tree}
          />
        </div>
        <div>
          <TreeCommitNavigationGraph />
          <MemoizedHardwareTested
            title={<FormattedMessage id="bootsTab.hardwareTested" />}
            environmentCompatible={hardwareData}
            diffFilter={diffFilter}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={data.summary.boots.status}
        />
        <TreeCommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={data.summary.boots.configs}
              diffFilter={diffFilter}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.summary.boots.architectures}
              diffFilter={diffFilter}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={data.summary.boots.issues}
              failedWithUnknownIssues={data.summary.boots.unknown_issues}
              diffFilter={diffFilter}
              issueFilterSection="bootIssue"
              detailsId={treeId}
              pageFrom={RedirectFrom.Tree}
            />
          </div>
          <div>
            <MemoizedHardwareTested
              title={<FormattedMessage id="bootsTab.hardwareTested" />}
              environmentCompatible={hardwareData}
              diffFilter={diffFilter}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <QuerySwitcher data={bootsData} status={fullStatus}>
        <BootsTable
          tableKey="treeDetailsBoots"
          filter={tableFilter.bootsTable}
          onClickFilter={onClickFilter}
          testHistory={bootsData ?? []}
          getRowLink={getRowLink}
          updatePathFilter={updatePathFilter}
          currentPathFilter={currentPathFilter}
          searchParams={searchParams}
        />
      </QuerySwitcher>
    </div>
  );
};

export default BootsTab;
