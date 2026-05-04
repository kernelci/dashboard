import { useCallback, type JSX } from 'react';

import FilterList from '@/components/FilterList/FilterList';
import { isTFilterKeys } from '@/types/general';
import type { TFilter, TFilterKeys } from '@/types/general';

const IGNORED_FILTERS: TFilterKeys[] = ['testPath', 'bootPath'];

interface IDetailsFilterList {
  filter: TFilter;
  flatFilter: string[];
  navigate: (filter: TFilter) => void;
  cleanFilters: () => void;
  isLoading: boolean;
}

export const createFlatFilter = (filter: TFilter): string[] => {
  const flatFilter: string[] = [];

  Object.entries(filter).forEach(([field, fieldValue]) => {
    // Type guard + don't show filters outside of the expected keys
    if (!isTFilterKeys(field)) {
      return;
    }

    if (IGNORED_FILTERS.includes(field)) {
      return;
    }

    if (typeof fieldValue === 'object') {
      Object.entries(fieldValue).forEach(([value, isSelected]) => {
        if (isSelected) {
          flatFilter.push(`${field}:${value}`);
        }
      });
    } else {
      flatFilter.push(`${field}:${fieldValue}`);
    }
  });
  return flatFilter;
};

const DetailsFilterList = ({
  filter,
  flatFilter,
  navigate,
  cleanFilters,
  isLoading = false,
}: IDetailsFilterList): JSX.Element => {
  const onClickItem = useCallback(
    (flatValue: string, _: number) => {
      const [field, ...rest] = flatValue.split(':');
      const value = rest.join(':');

      const newFilter = JSON.parse(JSON.stringify(filter ?? {}));
      const fieldSection = newFilter[field];

      if (typeof fieldSection === 'object') {
        delete fieldSection[value];
        if (Object.keys(fieldSection).length === 0) {
          delete newFilter[field];
        }
      } else {
        delete newFilter[field];
      }

      navigate(newFilter);
    },
    [filter, navigate],
  );

  return (
    <FilterList
      isLoading={isLoading}
      items={flatFilter}
      onClickItem={onClickItem}
      onClickCleanAll={cleanFilters}
      removeOnEmpty={true}
    />
  );
};

export default DetailsFilterList;
