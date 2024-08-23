import { useCallback, useMemo } from 'react';

import { useNavigate } from '@tanstack/react-router';

import FilterList from '@/components/FilterList/FilterList';
import { TFilter, TFilterKeys } from '@/types/tree/TreeDetails';

interface ITreeDetailsFilterList {
  filter: TFilter;
}

const createFlatFilter = (filter: TFilter): string[] => {
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

const TreeDetailsFilterList = ({
  filter,
}: ITreeDetailsFilterList): JSX.Element => {
  const flatFilter = useMemo(() => createFlatFilter(filter), [filter]);
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const onClickItem = useCallback(
    (flatValue: string, _: number) => {
      const [field, value] = flatValue.split(':');

      const newFilter = JSON.parse(JSON.stringify(filter ?? {}));
      const fieldSection = newFilter[field as TFilterKeys];

      if (typeof fieldSection === 'object') {
        delete fieldSection[value];
      } else {
        delete newFilter[field];
      }

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
    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          diffFilter: {},
        };
      },
    });
  }, [navigate]);

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
