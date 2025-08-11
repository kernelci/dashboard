import { memo, useMemo, type JSX } from 'react';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import type { TTreeTestsData } from '@/types/tree/TreeDetails';

import { ScrollArea } from '@/components/ui/scroll-area';

import type { TFilter } from '@/types/general';

import FilterLink from '@/components/Tabs/FilterLink';
import { sortByErrorsAndText } from '@/utils/utils';

interface IHardwareTested
  extends Pick<TTreeTestsData, 'environmentCompatible'> {
  title: IBaseCard['title'];
  diffFilter: TFilter;
}

const HardwareTested = ({
  environmentCompatible,
  title,
  diffFilter,
}: IHardwareTested): JSX.Element => {
  const sortedEnvironmentCompatibles = useMemo(() => {
    return Object.keys(environmentCompatible).sort((a, b) =>
      sortByErrorsAndText(
        { errors: environmentCompatible[a].FAIL ?? 0, text: a },
        { errors: environmentCompatible[b].FAIL ?? 0, text: b },
      ),
    );
  }, [environmentCompatible]);

  return (
    <BaseCard
      title={title}
      content={
        <ScrollArea className="h-[350px]">
          <DumbListingContent>
            {sortedEnvironmentCompatibles.map(hardwareTestedName => {
              const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } =
                environmentCompatible[hardwareTestedName];

              return (
                <FilterLink
                  key={hardwareTestedName}
                  filterValue={hardwareTestedName}
                  filterSection="hardware"
                  diffFilter={diffFilter}
                >
                  <ListingItem
                    hasBottomBorder
                    key={hardwareTestedName}
                    text={hardwareTestedName}
                    leftIcon={
                      <GroupedTestStatus
                        done={DONE}
                        fail={FAIL}
                        error={ERROR}
                        miss={MISS}
                        pass={PASS}
                        skip={SKIP}
                        nullStatus={NULL}
                      />
                    }
                  />
                </FilterLink>
              );
            })}
          </DumbListingContent>
        </ScrollArea>
      }
    />
  );
};

export const MemoizedHardwareTested = memo(HardwareTested);
