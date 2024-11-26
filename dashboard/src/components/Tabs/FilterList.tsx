import { useCallback, useMemo } from 'react';

import FilterList from '@/components/FilterList/FilterList';

interface IDetailsFilterList<
  T extends Record<string, Record<string, boolean | number>>,
> {
  filter: T;
  navigate: (filter: T) => void;
  cleanFilters: () => void;
}

const createFlatFilter = <
  T extends Record<string, Record<string, boolean | number>>,
>(
  filter: T,
): string[] => {
  const flatFilter: string[] = [];

  Object.entries(filter).forEach(([field, fieldValue]) => {
    if (typeof fieldValue === 'object') {
      Object.entries(fieldValue).forEach(([value, isSelected]) => {
        if (isSelected) flatFilter.push(`${field}:${value}`);
      });
    } else {
      flatFilter.push(`${field}:${fieldValue}`);
    }
  });
  return flatFilter;
};

const DetailsFilterList = <
  T extends Record<string, Record<string, boolean | number>>,
  K extends string,
>({
  filter,
  navigate,
  cleanFilters,
}: IDetailsFilterList<T>): JSX.Element => {
  const flatFilter = useMemo(() => createFlatFilter(filter), [filter]);

  const onClickItem = useCallback(
    (flatValue: string, _: number) => {
      const [field, ...rest] = flatValue.split(':');
      const value = rest.join(':');

      const newFilter = JSON.parse(JSON.stringify(filter ?? {})) as T;
      const fieldSection = newFilter[field as K];

      if (typeof fieldSection === 'object') {
        delete fieldSection[value];
      } else {
        delete newFilter[field];
      }

      navigate(newFilter);
    },
    [filter, navigate],
  );

  return (
    <FilterList
      items={flatFilter}
      onClickItem={onClickItem}
      onClickCleanAll={cleanFilters}
      removeOnEmpty={true}
    />
  );
};

export default DetailsFilterList;
