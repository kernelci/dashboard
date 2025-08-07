import { memo, useMemo, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import type { IListingItem } from '@/components/ListingItem/ListingItem';
import ListingItem from '@/components/ListingItem/ListingItem';
import { BuildStatus } from '@/components/Status/Status';
import BaseCard from '@/components/Cards/BaseCard';

import FilterLink from '@/components/Tabs/FilterLink';
import type { TFilter, TFilterObjectsKeys } from '@/types/general';
import { UNKNOWN_STRING } from '@/utils/constants/backend';

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
      configs.sort((a, b) => {
        const textA = a.text;
        const textB = b.text;

        if (textA === UNKNOWN_STRING && textA !== textB) {
          return 1;
        }
        if (textB === UNKNOWN_STRING && textB !== textA) {
          return -1;
        }

        const errorsA = a.errors ?? 0;
        const errorsB = b.errors ?? 0;

        if (errorsB !== errorsA) {
          return errorsB - errorsA;
        }

        return textA.localeCompare(textB);
      }),
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
