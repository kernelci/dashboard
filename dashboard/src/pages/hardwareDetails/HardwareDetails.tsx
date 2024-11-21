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

import { HardwareHeader } from './HardwareDetailsHeaderTable';
import HardwareDetailsTabs from './Tabs/HardwareDetailsTabs';

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
  const { treeIndexes, startTimestampInSeconds, endTimestampInSeconds } =
    useSearch({ from: '/hardware/$hardwareId' });
  const { hardwareId } = useParams({ from: '/hardware/$hardwareId' });
  const { origin } = useSearch({ from: '/hardware' });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

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
    treeIndexes ?? [],
  );

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
        <HardwareDetailsTabs
          HardwareDetailsData={data}
          hardwareId={hardwareId}
        />
      </div>
    </div>
  );
}

export default HardwareDetails;
