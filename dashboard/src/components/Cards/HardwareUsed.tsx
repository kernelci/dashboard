import { memo, useMemo, type JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';

import { Badge } from '@/components/ui/badge';
import type { TFilter } from '@/types/general';

import FilterLink from '@/components/Tabs/FilterLink';

interface IHardwareUsed {
  title: IBaseCard['title'];
  hardwareUsed?: string[];
  diffFilter: TFilter;
}

const HardwareLink = ({
  hardware,
  diffFilter,
}: {
  hardware: string;
  diffFilter: TFilter;
}): JSX.Element => {
  const { currentPageTab } = useSearch({ from: '/tree/$treeId' });
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
}: IHardwareUsed): JSX.Element => {
  const hardwareSorted = useMemo(() => hardwareUsed?.sort(), [hardwareUsed]);

  return (
    <BaseCard
      title={title}
      className="mb-0"
      content={
        <div className="flex flex-row flex-wrap gap-4 p-4">
          {hardwareSorted?.map(hardware => (
            <MemoizedHardwareLink
              key={hardware}
              hardware={hardware}
              diffFilter={diffFilter}
            />
          ))}
        </div>
      }
    />
  );
};

export default memo(HardwareUsed);
