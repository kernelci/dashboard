import type { HTMLProps, JSX } from 'react';
import { MdLink } from 'react-icons/md';

export const LinkIcon = ({
  className,
}: {
  className: HTMLProps<HTMLElement>['className'];
}): JSX.Element => {
  return <MdLink className={className} />;
};
