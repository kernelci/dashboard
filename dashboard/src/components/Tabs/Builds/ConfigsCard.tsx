import { memo, useMemo, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import type { IListingItem } from '@/components/ListingItem/ListingItem';
import ListingItem from '@/components/ListingItem/ListingItem';
import { BuildStatus } from '@/components/Status/Status';
import BaseCard from '@/components/Cards/BaseCard';

import FilterLink from '@/components/Tabs/FilterLink';
import type { TFilter, TFilterObjectsKeys } from '@/types/general';
import { sortByErrorsAndText } from '@/utils/utils';

interface IConfigsCard {
  configs: IListingItem[];
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
  diffFilter: TFilter;
}

const ConfigsCard = ({ configs, diffFilter }: IConfigsCard): JSX.Element => {
  const sortedConfigs = useMemo(
    () =>
      configs.sort((a, b) =>
        sortByErrorsAndText(
          { errors: a.errors ?? 0, text: a.text },
          { errors: b.errors ?? 0, text: b.text },
        ),
      ),
    [configs],
  );

  const content = useMemo(() => {
    return (
      <DumbListingContent>
        {sortedConfigs.map((item, i) => (
          <FilterLink
            key={i}
            filterSection="configs"
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
  }, [sortedConfigs, diffFilter]);

  return (
    <BaseCard
      title={<FormattedMessage id="global.configs" />}
      content={content}
    />
  );
};

export const MemoizedConfigsCard = memo(ConfigsCard);
