import { MdOutlineSearch } from 'react-icons/md';

import type { JSX } from 'react';

export const SearchIcon = ({
  className,
}: {
  className: HTMLElement['className'];
}): JSX.Element => <MdOutlineSearch className={className} />;
