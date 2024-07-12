import { useCallback, useMemo } from 'react';
import { IoClose } from 'react-icons/io5';
import classNames from 'classnames';
import { useIntl } from 'react-intl';

import { Button } from '../ui/button';

interface IFilterList {
  itens: string[];
  onClickItem: (itemIdx: number) => void;
  onClickCleanAll: () => void;
  removeOnEmpty?: boolean;
}

interface IFilterItem extends IFilterButton {
  idx: number;
  onClickItem: (idx: number) => void;
}

export interface IFilterButton
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  text: string;
  variant?: 'primary' | 'secondary';
  className?: string;
}

const baseButtonClassNames =
  'text-sm h-10 pr-2 rounded-md flex items-center bg-darkGray hover:bg-mediumGray';
const primaryClassNames = 'bg-lightBlue text-white';
const secondaryClassNames = 'bg-darkGray text-black';

const FilterButton = ({
  text,
  variant = 'secondary',
  className,
  ...props
}: IFilterButton): JSX.Element => {
  const buttonClassNames = classNames(
    baseButtonClassNames,
    variant === 'primary' ? primaryClassNames : secondaryClassNames,
    className,
  );

  return (
    <Button className={buttonClassNames} {...props}>
      {text}
      <IoClose className="size-6" />
    </Button>
  );
};

const FilterItem = ({
  text,
  variant,
  onClickItem,
  idx,
  ...props
}: IFilterItem): JSX.Element => {
  const onClickHandler = useCallback(
    () => onClickItem(idx),
    [onClickItem, idx],
  );

  return (
    <FilterButton
      text={text}
      variant={variant}
      onClick={onClickHandler}
      {...props}
    />
  );
};

const FilterList = ({
  itens,
  onClickItem,
  onClickCleanAll,
  removeOnEmpty = false,
}: IFilterList): JSX.Element => {
  const intl = useIntl();

  const buttonList = useMemo(
    () =>
      itens.map((item, idx) => (
        <FilterItem
          key={idx + item}
          text={item}
          onClickItem={onClickItem}
          idx={idx}
        />
      )),
    [itens, onClickItem],
  );

  if (removeOnEmpty && !itens) {
    return <></>;
  }

  return (
    <div className="flex flex-wrap gap-4">
      {buttonList}
      <FilterButton
        text={intl.formatMessage({ id: 'global.cleanAll' })}
        variant="primary"
        onClick={onClickCleanAll}
      />
    </div>
  );
};

export default FilterList;
