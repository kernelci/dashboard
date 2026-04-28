import { MdChevronRight } from 'react-icons/md';

import type { JSX } from 'react';

interface ChevronRightAnimateProps {
  isExpanded?: boolean;
  animated?: boolean;
  className?: string;
}

export const ChevronRightAnimate = ({
  isExpanded,
  animated = true,
  className = '',
}: ChevronRightAnimateProps): JSX.Element => {
  const baseClass = 'transition';
  const animationClass = animated
    ? "group-data-[state='open']:rotate-90"
    : '';
  const expandedClass = isExpanded !== undefined && isExpanded ? 'rotate-90' : '';

  return (
    <MdChevronRight
      className={`${baseClass} ${animationClass} ${expandedClass} ${className}`.trim()}
    />
  );
};
