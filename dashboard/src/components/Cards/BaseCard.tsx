import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

type CommonProps = {
  title: ReactNode;
  className?: string;
};

type WithChildren = {
  children: ReactNode;
  content?: never;
} & CommonProps;

type WithContent = {
  children?: never;
  content: ReactNode;
} & CommonProps;

export type IBaseCard = WithChildren | WithContent;

export const BaseCard = ({
  title,
  content,
  className,
  children,
}: IBaseCard): JSX.Element => {
  return (
    <div
      className={cn(
        'mb-6 flex h-fit w-full break-inside-avoid-column flex-col gap-2 rounded-xl border border-darkGray bg-white pt-4 text-black',
        className,
      )}
    >
      <div className="border-b border-darkGray pb-2 pl-3 font-bold">
        {title}
      </div>
      <div>{children ? children : content}</div>
    </div>
  );
};

export default BaseCard;
