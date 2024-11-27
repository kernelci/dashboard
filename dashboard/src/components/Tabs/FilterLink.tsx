import { Link } from '@tanstack/react-router';

import { useDiffFilterParams } from '@/components/Tabs/tabsUtils';
import type { TFilter, TFilterObjectsKeys } from '@/types/general';

interface FilterLinkProps {
  children?: JSX.Element | string;
  filterValue: string;
  filterSection: TFilterObjectsKeys;
  diffFilter: TFilter;
  className?: string;
  disabled?: boolean; // temporary solution
}

const FilterLink = ({
  children,
  filterSection,
  filterValue,
  className,
  diffFilter,
  disabled,
}: FilterLinkProps): JSX.Element => {
  const handleDiffFilter = useDiffFilterParams(
    filterValue,
    filterSection,
    diffFilter,
  );

  return (
    <Link
      search={previousParams => ({
        ...previousParams,
        diffFilter: handleDiffFilter,
      })}
      disabled={disabled}
      key={filterValue}
      className={className}
    >
      {children}
    </Link>
  );
};

export default FilterLink;
