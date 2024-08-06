import cls from 'classnames';

import { useCallback, useMemo } from 'react';

import Checkbox from '../Checkbox/Checkbox';

type TOnClickItem = (value: string, isChecked: boolean) => void;

type TItems = { [key: string]: boolean };

interface ICheckboxSectionItem {
  value: string;
  onClickItem: TOnClickItem;
  isSelected: boolean;
}

interface ICheckboxList {
  items: TItems;
  onClickItem: TOnClickItem;
}

interface ICheckboxSubsection {
  items: TItems;
  title: string;
  onClickItem: TOnClickItem;
}

export interface ICheckboxSection {
  items?: TItems;
  title: string;
  subtitle?: string;
  subsections?: ICheckboxSubsection[];
  onClickItem: TOnClickItem;
  className?: string;
}

const CheckboxSectionItem = ({
  value,
  onClickItem,
  isSelected,
}: ICheckboxSectionItem): JSX.Element => {
  const handleOnToggle = useCallback(
    (isChecked: boolean) => onClickItem(value, isChecked),
    [value, onClickItem],
  );
  return (
    <Checkbox
      onToggle={handleOnToggle}
      text={value}
      startChecked={isSelected}
    />
  );
};

const CheckboxList = ({ items, onClickItem }: ICheckboxList): JSX.Element => {
  const itemComponents = useMemo(
    () =>
      Object.keys(items).map(key => (
        <CheckboxSectionItem
          key={key}
          value={key}
          onClickItem={onClickItem}
          isSelected={items[key]}
        />
      )),
    [items, onClickItem],
  );

  return (
    <div className="flex max-w-[1000px] flex-wrap gap-x-4 gap-y-6">
      {itemComponents}
    </div>
  );
};

const CheckboxSubsection = ({
  title,
  items,
  onClickItem,
}: ICheckboxSubsection): JSX.Element => {
  return (
    <div>
      <h4 className="mb-2 mt-6 text-sm font-medium text-dimGray">{title}</h4>
      <CheckboxList items={items} onClickItem={onClickItem} />
    </div>
  );
};

const CheckboxSection = ({
  items,
  title,
  subtitle,
  onClickItem,
  subsections,
  className,
}: ICheckboxSection): JSX.Element => {
  const subsectionComponents = useMemo(
    () =>
      subsections?.map(subsection => (
        <CheckboxSubsection
          key={subsection.title}
          title={subsection.title}
          items={subsection.items}
          onClickItem={subsection.onClickItem}
        />
      )),
    [subsections],
  );

  return (
    <div className={cls(className)}>
      <h3 className="mb-2 text-xl font-semibold text-dimGray">{title}</h3>
      <h4 className="mb-6 text-sm text-dimGray">{subtitle}</h4>
      {items && <CheckboxList items={items} onClickItem={onClickItem} />}
      {subsectionComponents}
    </div>
  );
};

export default CheckboxSection;
