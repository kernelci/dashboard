import { useCallback, useMemo } from 'react';

import FilterList from '@/components/FilterList/FilterList';

import { TFilter, TFilterKeys } from './TreeDetailsFilter';

interface ITreeDetailsFilterList {
  filter: TFilter;
  onFilter: (filter: TFilter) => void;
}

const createFlatFilter = (filter: TFilter): string[] => {
  const flatFilter: string[] = [];

  Object.entries(filter).forEach(([field, values]) => {
    Object.entries(values).forEach(([value, isSelected]) => {
      if (isSelected) flatFilter.push(`${field}:${value}`);
    });
  });
  return flatFilter;
};

const TreeDetailsFilterList = ({
  filter,
  onFilter,
}: ITreeDetailsFilterList): JSX.Element => {
  const flatFilter = useMemo(() => createFlatFilter(filter), [filter]);

  const onClickItem = useCallback(
    (flatValue: string, _: number) => {
      const [field, value] = flatValue.split(':');
      const newFilter = { ...filter };
      newFilter[field as TFilterKeys][value] = false;
      onFilter(newFilter);
    },
    [filter, onFilter],
  );

  const onClickCleanALl = useCallback(() => {
    const newFilter = { ...filter };

    flatFilter.forEach(flatValue => {
      const [field, value] = flatValue.split(':');
      newFilter[field as TFilterKeys][value] = false;
    });

    onFilter(newFilter);
  }, [filter, onFilter, flatFilter]);

  return (
    <FilterList
      items={flatFilter}
      onClickItem={onClickItem}
      onClickCleanAll={onClickCleanALl}
      removeOnEmpty={true}
    />
  );
};

export default TreeDetailsFilterList;
