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
import type { MessagesKey } from '@/locales/messages';

interface IFilterCard {
  data: Record<string, RequiredStatusCount>;
  diffFilter: TFilter;
  filterSection: TFilterObjectsKeys;
  hideSingleValue?: boolean;
  cardTitle: MessagesKey;
}

const FilterCard = ({
  data,
  diffFilter,
  filterSection,
  hideSingleValue = true,
  cardTitle,
}: IFilterCard): JSX.Element => {
  const content: JSX.Element[] = useMemo(() => {
    return Object.keys(data).map(item => {
      const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } = data[item];

      return (
        <FilterLink
          key={item}
          filterValue={item}
          filterSection={filterSection}
          diffFilter={diffFilter}
        >
          <ListingItem
            hasBottomBorder
            key={item}
            text={item}
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
  }, [data, filterSection, diffFilter]);

  if (hideSingleValue && Object.keys(data).length === 1) {
    return <></>;
  }

  return (
    <BaseCard title={<FormattedMessage id={cardTitle} />}>
      <DumbListingContent>{content}</DumbListingContent>
    </BaseCard>
  );
};

export const MemoizedFilterCard = memo(FilterCard);
