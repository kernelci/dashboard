import { memo, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import { DumbListingContent } from '../../ListingContent/ListingContent';
import ListingItem from '../../ListingItem/ListingItem';
import { BuildStatus } from '../../Status/Status';
import BaseCard from '../../Cards/BaseCard';

import FilterLink from '../FilterLink';

interface IConfigsCard<T> {
  configs: ITreeDetails['configs'];
  toggleFilterBySection: (value: string, filterSection: T) => void;
  diffFilter: Record<string, Record<string, boolean>>;
}

const ConfigsCard = <T,>({
  configs,
  diffFilter,
}: IConfigsCard<T>): JSX.Element => {
  const content = useMemo(() => {
    return (
      <DumbListingContent>
        {configs.map((item, i) => (
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
  }, [configs, diffFilter]);

  return (
    <BaseCard
      title={<FormattedMessage id="global.configs" />}
      content={content}
    />
  );
};

export const MemoizedConfigsCard = memo(ConfigsCard) as <T>(
  props: IConfigsCard<T>,
) => JSX.Element;
