import { memo, useMemo, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import BaseCard from '@/components/Cards/BaseCard';

import FilterLink from '@/components/Tabs/FilterLink';
import type {
  RequiredStatusCount,
  TFilter,
  TFilterObjectsKeys,
} from '@/types/general';

interface IOriginsCard {
  origins: Record<string, RequiredStatusCount>;
  diffFilter: TFilter;
  filterSection: TFilterObjectsKeys;
  hideSingleOrigin?: boolean;
}

const OriginsCard = ({
  origins,
  diffFilter,
  filterSection,
  hideSingleOrigin = true,
}: IOriginsCard): JSX.Element => {
  const content: JSX.Element[] = useMemo(() => {
    return Object.keys(origins).map(originItem => {
      const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } = origins[originItem];

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
    });
  }, [origins, filterSection, diffFilter]);

  if (hideSingleOrigin && Object.keys(origins).length === 1) {
    return <></>;
  }

  return (
    <BaseCard title={<FormattedMessage id="filter.origins" />}>
      <DumbListingContent>{content}</DumbListingContent>
    </BaseCard>
  );
};

export const MemoizedOriginsCard = memo(OriginsCard);
