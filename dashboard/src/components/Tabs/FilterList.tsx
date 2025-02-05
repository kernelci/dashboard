import { useCallback, useMemo } from 'react';

import FilterList from '@/components/FilterList/FilterList';
import type { TFilter } from '@/types/general';

interface IDetailsFilterList {
  filter: TFilter;
  navigate: (filter: TFilter) => void;
  cleanFilters: () => void;
  isLoading: boolean;
}

const createFlatFilter = (filter: TFilter): string[] => {
  const flatFilter: string[] = [];

  Object.entries(filter).forEach(([field, fieldValue]) => {
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
  navigate,
  cleanFilters,
  isLoading = false,
}: IDetailsFilterList): JSX.Element => {
  const flatFilter = useMemo(() => createFlatFilter(filter), [filter]);

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
