//TODO: make this component reusable for TreeDetails and HardwareDetails

import { Link } from '@tanstack/react-router';

import { useDiffFilterParams } from './tabsUtils';

interface FilterLinkProps<
  Keys extends string,
  Filter extends Record<Keys, Record<string, boolean>>,
> {
  children?: JSX.Element | string;
  filterValue: string;
  filterSection: Keys;
  diffFilter: Filter;
  className?: string;
}

const FilterLink = <
  Keys extends string,
  Filter extends Record<Keys, Record<string, boolean>>,
>({
  children,
  filterSection,
  filterValue,
  className,
  diffFilter,
}: FilterLinkProps<Keys, Filter>): JSX.Element => {
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
      key={filterValue}
      className={className}
    >
      {children}
    </Link>
  );
};

export default FilterLink;
