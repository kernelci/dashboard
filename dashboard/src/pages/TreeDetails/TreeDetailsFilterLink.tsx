import { Link } from '@tanstack/react-router';

import { TFilterObjectsKeys } from '@/types/tree/TreeDetails';

import { useDiffFilterParams } from './treeDetailsUtils';

interface FilterLinkProps {
  children?: JSX.Element | string;
  filterValue: string;
  filterSection: TFilterObjectsKeys;
  className?: string;
}

const FilterLink = ({
  children,
  filterSection,
  filterValue,
  className,
}: FilterLinkProps): JSX.Element => {
  const diffFilter = useDiffFilterParams(filterValue, filterSection);

  return (
    <Link
      search={previousParams => ({
        ...previousParams,
        diffFilter,
      })}
      key={filterValue}
      className={className}
    >
      {children}
    </Link>
  );
};

export default FilterLink;
