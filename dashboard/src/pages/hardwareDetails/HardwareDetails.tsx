import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo } from 'react';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';

import { Skeleton } from '@/components/Skeleton';
import { useHardwareDetails } from '@/api/hardwareDetails';

import type { Trees } from '@/types/hardware/hardwareDetails';

import {
  GroupedTestStatus,
  BuildStatus as BuildStatusComponent,
} from '@/components/Status/Status';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import DetailsFilterList from '@/components/Tabs/FilterList';

import type { TFilter } from '@/types/general';

import { HardwareHeader } from './HardwareDetailsHeaderTable';
import type { TreeDetailsTabRightElement } from './Tabs/HardwareDetailsTabs';
import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';
import HardwareDetailsFilter from './HardwareDetailsFilter';

const sanitizeTreeItems = (treeItems: Trees[]): Trees[] =>
  treeItems.map(tree => ({
    treeName: tree['treeName'] ?? '-',
    gitRepositoryBranch: tree['gitRepositoryBranch'] ?? '-',
    headGitCommitName: tree['headGitCommitName'] ?? '-',
    headGitCommitHash: tree['headGitCommitHash'] ?? '-',
    gitRepositoryUrl: tree['gitRepositoryUrl'] ?? '-',
    index: tree['index'],
  }));

function HardwareDetails(): JSX.Element {
  const {
    treeIndexes,
    treeCommits,
    limitTimestampInSeconds,
    diffFilter,
    origin,
  } = useSearch({ from: '/hardware/$hardwareId' });

  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const reqFilter = mapFilterToReq(diffFilter);

  const updateTreeFilters = useCallback(
    (selectedIndexes: number[]) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          treeIndexes: selectedIndexes,
        }),
      });
    },
    [navigate],
  );

  const onFilterChange = useCallback(
    (newFilter: TFilter) => {
      navigate({
        search: previousSearch => {
          return {
            ...previousSearch,
            diffFilter: newFilter,
          };
        },
      });
    },
    [navigate],
  );

  const cleanAll = useCallback(() => {
    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          diffFilter: {},
        };
      },
    });
  }, [navigate]);

  const { data, isLoading, isPlaceholderData } = useHardwareDetails(
    hardwareId,
    limitTimestampInSeconds,
    origin,
    reqFilter,
    treeIndexes ?? [],
    treeCommits,
  );

  const filterListElement = useMemo(
    () => (
      <DetailsFilterList
        filter={diffFilter}
        cleanFilters={cleanAll}
        navigate={onFilterChange}
        isLoading={isPlaceholderData}
      />
    ),
    [cleanAll, diffFilter, isPlaceholderData, onFilterChange],
  );

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = data?.builds.summary.builds ?? {};
    const { statusSummary: testStatusSummary } = data?.tests ?? {};

    const { statusSummary: bootStatusSummary } = data?.boots ?? {};

    return {
      'global.tests': testStatusSummary ? (
        <GroupedTestStatus
          fail={testStatusSummary.FAIL}
          pass={testStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'global.boots': bootStatusSummary ? (
        <GroupedTestStatus
          fail={bootStatusSummary.FAIL}
          pass={bootStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'global.builds': data?.builds ? (
        <BuildStatusComponent
          valid={valid}
          invalid={invalid}
          hideInconclusive
        />
      ) : (
        <></>
      ),
    };
  }, [data?.boots, data?.builds, data?.tests]);

  const treeData = useMemo(
    () => sanitizeTreeItems(data?.trees || []),
    [data?.trees],
  );

  if (isLoading || !data)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return (
    <div className="flex flex-col pt-8">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink
              to="/hardware"
              search={previousParams => {
                return {
                  intervalInDays: previousParams.intervalInDays,
                  origin: previousParams.origin,
                  hardwareSearch: previousParams.hardwareSearch,
                };
              }}
            >
              <FormattedMessage id="hardware.path" />
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>
              <span>{hardwareId}</span>
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <div className="mt-5">
        <HardwareHeader
          treeItems={treeData}
          selectedIndexes={treeIndexes}
          updateTreeFilters={updateTreeFilters}
        />
        <div className="flex flex-col pb-2">
          <div className="sticky top-[4.5rem] z-10">
            <div className="absolute right-0 top-2 py-4">
              <HardwareDetailsFilter
                paramFilter={diffFilter}
                hardwareName={hardwareId}
                data={data}
              />
            </div>
          </div>
          <HardwareDetailsTabs
            hardwareDetailsData={data}
            hardwareId={hardwareId}
            filterListElement={filterListElement}
            countElements={tabsCounts}
          />
        </div>
      </div>
    </div>
  );
}

export default HardwareDetails;
