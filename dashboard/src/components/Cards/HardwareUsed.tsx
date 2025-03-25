import { memo, useMemo, type JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import type { UseQueryResult } from '@tanstack/react-query';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';

import { Badge } from '@/components/ui/badge';
import type { TFilter } from '@/types/general';

import FilterLink from '@/components/Tabs/FilterLink';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

interface IHardwareUsed {
  title: IBaseCard['title'];
  hardwareUsed?: string[];
  diffFilter: TFilter;
  queryStatus: UseQueryResult['status'];
}

const HardwareLink = ({
  hardware,
  diffFilter,
}: {
  hardware: string;
  diffFilter: TFilter;
}): JSX.Element => {
  const { currentPageTab } = useSearch({ from: '/_main/tree/$treeId' });
  return (
    <FilterLink
      filterValue={hardware}
      filterSection="hardware"
      diffFilter={diffFilter}
      to={`/tree/$treeId`}
      from={`/tree/$treeId`}
      key={currentPageTab}
    >
      <Badge variant="outline" className="text-sm font-normal">
        {hardware}
      </Badge>
    </FilterLink>
  );
};

const MemoizedHardwareLink = memo(HardwareLink);

const HardwareUsed = ({
  hardwareUsed,
  title,
  diffFilter,
  queryStatus,
}: IHardwareUsed): JSX.Element => {
  const hardwareSorted = useMemo(() => hardwareUsed?.sort(), [hardwareUsed]);

  return (
    <BaseCard
      title={title}
      className="mb-0 gap-0"
      content={
        <QuerySwitcher
          status={queryStatus}
          data={hardwareUsed}
          skeletonClassname="h-[50px]"
        >
          <div className="flex flex-row flex-wrap gap-4 p-4">
            {hardwareSorted?.map(hardware => (
              <MemoizedHardwareLink
                key={hardware}
                hardware={hardware}
                diffFilter={diffFilter}
              />
            ))}
          </div>
        </QuerySwitcher>
      }
    />
  );
};

export default memo(HardwareUsed);
