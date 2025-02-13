import { memo, useMemo, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type { TFilter, TFilterObjectsKeys } from '@/types/general';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import ListingItem, {
  type IListingItem,
} from '@/components/ListingItem/ListingItem';
import FilterLink from '@/components/Tabs/FilterLink';
import { BuildStatus } from '@/components/Status/Status';

import BaseCard from './BaseCard';

interface IPlatformsCard {
  platforms: IListingItem[];
  issueFilterSection: TFilterObjectsKeys;
  diffFilter: TFilter;
}

const PlatformsCard = ({
  platforms,
  issueFilterSection,
  diffFilter,
}: IPlatformsCard): JSX.Element => {
  const content = useMemo(() => {
    return (
      <DumbListingContent>
        {platforms.map((item, i) => (
          <FilterLink
            key={i}
            filterSection={issueFilterSection}
            filterValue={item.text}
            diffFilter={diffFilter}
          >
            <ListingItem
              text={item.text}
              leftIcon={
                <BuildStatus
                  valid={item.success}
                  invalid={item.errors}
                  unknown={item.unknown}
                />
              }
            />
          </FilterLink>
        ))}
      </DumbListingContent>
    );
  }, [platforms, diffFilter, issueFilterSection]);

  return (
    <BaseCard
      title={<FormattedMessage id="hardwareDetails.platforms" />}
      content={content}
    />
  );
};

export const MemoizedPlatformsCard = memo(PlatformsCard);
