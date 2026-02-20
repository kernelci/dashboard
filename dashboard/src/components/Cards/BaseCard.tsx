import type { ReactNode, JSX } from 'react';

import { cn } from '@/lib/utils';

type CommonProps = {
  title: ReactNode;
  className?: string;
  'data-test-id'?: string;
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
  'data-test-id': dataTestId,
}: IBaseCard): JSX.Element => {
  return (
    <div
      className={cn(
        'border-dark-gray mb-6 flex h-fit w-full break-inside-avoid-column flex-col gap-2 rounded-xl border bg-white pt-4 text-black',
        className,
      )}
      data-test-id={dataTestId}
    >
      <div className="border-dark-gray border-b pb-2 pl-3 font-bold">
        {title}
      </div>
      <div>{children ? children : content}</div>
    </div>
  );
};

export default BaseCard;
