import { MdChevronRight } from 'react-icons/md';

import type { JSX } from 'react';

export const ChevronRightAnimate = (): JSX.Element => {
  return (
    <MdChevronRight className="transition group-data-[state='open']:rotate-90" />
  );
};
