import { ReactElement } from 'react';
import classNames from 'classnames';

interface IBaseCard {
  title: ReactElement;
  content: ReactElement;
  className?: string;
}

const containerClassName =
  'flex flex-col rounded-xl bg-white w-full h-fit border border-darkGray text-black break-inside-avoid-column mb-6';

const BaseCard = ({ title, content, className }: IBaseCard): JSX.Element => {
  return (
    <div className={classNames(containerClassName, className)}>
      <div className="flex flex-col w-full h-full pt-4 gap-2">
        <span className="font-bold border-b border-darkGray pb-2 pl-3">
          {title}
        </span>
        {content}
      </div>
    </div>
  );
};

export default BaseCard;
