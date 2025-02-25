import { memo, useMemo, type JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import { Badge } from '@/components/ui/badge';

import FilterLink from '@/components/Tabs/FilterLink';

import type { TFilter } from '@/types/general';

import BaseCard, { type IBaseCard } from './BaseCard';

interface ICompatible {
  title: IBaseCard['title'];
  compatibles: string[];
  diffFilter: TFilter;
}

const CompatibleLink = ({
  compatible,
  diffFilter,
}: {
  compatible: string;
  diffFilter: TFilter;
}): JSX.Element => {
  const { currentPageTab } = useSearch({ from: '/_main/hardware/$hardwareId' });
  return (
    <FilterLink
      filterValue={compatible}
      filterSection="hardware"
      diffFilter={diffFilter}
      to={`/hardware/$hardwareId`}
      from={`/hardware/$hardwareId`}
      key={currentPageTab}
    >
      <Badge variant="outline" className="text-sm font-normal">
        {compatible}
      </Badge>
    </FilterLink>
  );
};

const MemoizedCompatibleLink = memo(CompatibleLink);

const CompatibleHardware = ({
  title,
  compatibles,
  diffFilter,
}: ICompatible): JSX.Element => {
  const compatiblesSorted = useMemo(() => compatibles.sort(), [compatibles]);

  return (
    <BaseCard
      title={title}
      className="mb-0"
      content={
        <div className="flex flex-row flex-wrap gap-4 p-4">
          {compatiblesSorted.map(compatible => (
            <MemoizedCompatibleLink
              key={compatible}
              compatible={compatible}
              diffFilter={diffFilter}
            />
          ))}
        </div>
      }
    />
  );
};

export default memo(CompatibleHardware);
