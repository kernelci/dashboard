import type { HTMLProps, JSX } from 'react';
import { HiOutlineExternalLink } from 'react-icons/hi';

export const ExternalLinkIcon = ({
  className,
}: {
  className?: HTMLProps<HTMLElement>['className'];
}): JSX.Element => {
  return <HiOutlineExternalLink className={className} />;
};
