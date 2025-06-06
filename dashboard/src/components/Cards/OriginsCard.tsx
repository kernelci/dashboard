import { memo, useMemo, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import BaseCard from '@/components/Cards/BaseCard';

import FilterLink from '@/components/Tabs/FilterLink';
import type { TFilter, TFilterObjectsKeys } from '@/types/general';
import type { Summary } from '@/types/commonDetails';

interface IOriginsCard {
  origins: Summary['builds']['origins'];
  diffFilter: TFilter;
  filterSection: TFilterObjectsKeys;
}

const OriginsCard = ({
  origins,
  diffFilter,
  filterSection,
}: IOriginsCard): JSX.Element => {
  const content = useMemo(() => {
    return (
      <DumbListingContent>
        {Object.keys(origins).map(originItem => {
          const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } =
            origins[originItem];

          return (
            <FilterLink
              key={originItem}
              filterValue={originItem}
              filterSection={filterSection}
              diffFilter={diffFilter}
            >
              <ListingItem
                hasBottomBorder
                key={originItem}
                text={originItem}
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
    );
  }, [origins, filterSection, diffFilter]);

  return (
    <BaseCard
      title={<FormattedMessage id="filter.origins" />}
      content={content}
    />
  );
};

export const MemoizedOriginsCard = memo(OriginsCard);
