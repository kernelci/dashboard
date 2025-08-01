import { memo, useMemo, type JSX } from 'react';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import type { TTreeTestsData } from '@/types/tree/TreeDetails';

import FilterLink from '@/components/Tabs/FilterLink';
import type { TFilter } from '@/types/general';
import { UNKNOWN_STRING } from '@/utils/constants/backend';

interface IConfigList extends Pick<TTreeTestsData, 'configStatusCounts'> {
  title: IBaseCard['title'];
  diffFilter: TFilter;
}

const ConfigsList = ({
  configStatusCounts,
  title,
  diffFilter,
}: IConfigList): JSX.Element => {
  const sortedConfigStatusCounts = useMemo(
    () =>
      Object.keys(configStatusCounts).sort((a, b) => {
        if (a === UNKNOWN_STRING) {
          return 1;
        }
        if (b === UNKNOWN_STRING) {
          return -1;
        }

        const failA = configStatusCounts[a].FAIL ?? 0;
        const failB = configStatusCounts[b].FAIL ?? 0;

        if (failB !== failA) {
          return failB - failA;
        }

        return a.localeCompare(b);
      }),
    [configStatusCounts],
  );

  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {sortedConfigStatusCounts.map(configName => {
            const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } =
              configStatusCounts[configName];
            return (
              <FilterLink
                key={configName}
                filterSection="configs"
                filterValue={configName}
                diffFilter={diffFilter}
              >
                <ListingItem
                  hasBottomBorder
                  key={configName}
                  text={configName}
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
      }
    />
  );
};

const MemoizedConfigList = memo(ConfigsList);
export default MemoizedConfigList;
