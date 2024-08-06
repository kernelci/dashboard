import { ReactElement, ReactNode } from 'react';
import classNames from 'classnames';

interface IBaseCard {
  title: ReactNode;
  content: ReactElement;
  className?: string;
}

const containerClassName =
  'flex flex-col rounded-xl bg-white w-full h-fit border border-darkGray text-black break-inside-avoid-column mb-6';

const BaseCard = ({ title, content, className }: IBaseCard): JSX.Element => {
  return (
    <div className={classNames(containerClassName, className)}>
      <div className="flex h-full w-full flex-col gap-2 pt-4">
        <span className="border-b border-darkGray pb-2 pl-3 font-bold">
          {title}
        </span>
        {content}
      </div>
    </div>
  );
};

export default BaseCard;
