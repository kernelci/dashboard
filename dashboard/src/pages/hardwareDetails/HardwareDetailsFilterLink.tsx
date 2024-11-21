//TODO: make this component reusable for TreeDetails and HardwareDetails

import { Link } from '@tanstack/react-router';

import type { TFilterObjectsKeys } from '@/types/hardware/hardwareDetails';

import { useDiffFilterParams } from './hardwareDetailsUtils';

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
      disabled
      key={filterValue}
      className={className}
    >
      {children}
    </Link>
  );
};

export default FilterLink;
