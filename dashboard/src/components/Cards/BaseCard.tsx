import { ReactElement } from 'react';
import classNames from 'classnames';

interface IBaseCard {
  title: string;
  content: ReactElement;
  className?: string;
}

const containerClassName =
  'flex flex-col rounded-xl bg-white w-1/2 h-fit border border-darkGray text-black';

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
