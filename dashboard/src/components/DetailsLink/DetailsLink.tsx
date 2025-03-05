import { type JSX, memo } from 'react';

import { Link, type LinkProps } from '@tanstack/react-router';

const LinkItem = ({ children, ...props }: LinkProps): JSX.Element => {
  return (
    <Link
      {...props}
      className="flex flex-row items-center gap-1 underline hover:text-slate-900"
      target="_blank"
      rel="noreferrer"
    >
      {children}
    </Link>
  );
};

export default memo(LinkItem);
