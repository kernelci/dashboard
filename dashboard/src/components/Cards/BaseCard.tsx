import { ReactElement, ReactNode } from 'react';

import { cn } from '@/lib/utils';

export interface IBaseCard {
  title: ReactNode;
  content: ReactElement;
  className?: string;
}

const BaseCard = ({ title, content, className }: IBaseCard): JSX.Element => {
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
      <div>{content}</div>
    </div>
  );
};

export default BaseCard;
