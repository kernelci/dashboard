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

import { HardwareHeader } from './HardwareDetailsHeaderTable';
import type { TreeDetailsTabRightElement } from './Tabs/HardwareDetailsTabs';
import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';
import HardwareDetailsFilter, { mapFilterToReq } from './HardwareDetailsFilter';
import HardwareDetailsFilterList from './HardwareDetailsFilterList';

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
    startTimestampInSeconds,
    endTimestampInSeconds,
    diffFilter,
  } = useSearch({ from: '/hardware/$hardwareId' });
  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });
  const { origin } = useSearch({ from: '/hardware' });

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

  const { data, isLoading } = useHardwareDetails(
    hardwareId,
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
    reqFilter,
    treeIndexes ?? [],
  );

  const filterListElement = useMemo(
    () => <HardwareDetailsFilterList filter={diffFilter} />,
    [diffFilter],
  );

  const tabsCounts: TreeDetailsTabRightElement = useMemo(() => {
    const { valid, invalid } = data?.builds.summary.builds ?? {};
    const { statusSummary: testStatusSummary } = data?.tests ?? {};

    const { statusSummary: bootStatusSummary } = data?.boots ?? {};

    return {
      'treeDetails.tests': testStatusSummary ? (
        <GroupedTestStatus
          fail={testStatusSummary.FAIL}
          pass={testStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'treeDetails.boots': bootStatusSummary ? (
        <GroupedTestStatus
          fail={bootStatusSummary.FAIL}
          pass={bootStatusSummary.PASS}
          hideInconclusive
        />
      ) : (
        <></>
      ),
      'treeDetails.builds': data?.builds ? (
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
        <div className="relative pt-2">
          <div className="absolute right-0 top-0">
            <HardwareDetailsFilter
              paramFilter={diffFilter}
              hardwareName={hardwareId}
              data={data}
            />
          </div>
          <HardwareDetailsTabs
            HardwareDetailsData={data}
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
