import { useCallback, useMemo } from 'react';

import { useNavigate } from '@tanstack/react-router';

import FilterList from '@/components/FilterList/FilterList';
import { TFilter, TFilterKeys } from '@/types/tree/TreeDetails';

interface ITreeDetailsFilterList {
  filter: TFilter;
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
}: ITreeDetailsFilterList): JSX.Element => {
  const flatFilter = useMemo(() => createFlatFilter(filter), [filter]);
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const onClickItem = useCallback(
    (flatValue: string, _: number) => {
      const [field, value] = flatValue.split(':');
      const newFilter = { ...filter };
      newFilter[field as TFilterKeys][value] = false;

      navigate({
        search: previousSearch => {
          return {
            ...previousSearch,
            diffFilter: newFilter,
          };
        },
      });
    },
    [filter, navigate],
  );

  const onClickCleanALl = useCallback(() => {
    const newFilter = { ...filter };

    flatFilter.forEach(flatValue => {
      const [field, value] = flatValue.split(':');
      newFilter[field as TFilterKeys][value] = false;
    });

    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          diffFilter: newFilter,
        };
      },
    });
  }, [filter, flatFilter, navigate]);

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
