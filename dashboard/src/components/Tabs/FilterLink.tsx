import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import type { JSX } from 'react';

import { useDiffFilterParams } from '@/components/Tabs/tabsUtils';
import type { TFilter, TFilterObjectsKeys } from '@/types/general';

interface FilterLinkProps {
  children?: JSX.Element | string;
  filterValue: string;
  filterSection: TFilterObjectsKeys;
  diffFilter: TFilter;
  className?: string;
  from?: LinkProps['from'];
  // TODO: make linter accept the LinkProps['to'] type
  to?: LinkProps['to'] | (string & {});
}

const FilterLink = ({
  children,
  filterSection,
  filterValue,
  className,
  from,
  to,
  diffFilter,
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
      state={s => s}
      from={from}
      to={to}
      key={filterValue}
      className={className}
    >
      {children}
    </Link>
  );
};

export default FilterLink;
