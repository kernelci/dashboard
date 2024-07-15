import cls from 'classnames';

import { useCallback, useMemo } from 'react';

import Checkbox from '../Checkbox/Checkbox';

type TOnClickItem = (itemIdx: number, isChecked: boolean) => void;

interface ICheckboxSectionItem {
  text: string;
  onClickItem: TOnClickItem;
  idx: number;
}

interface ICheckboxList {
  items: string[];
  onClickItem: TOnClickItem;
}

interface ICheckboxSubsection {
  items: string[];
  title: string;
  onClickItem: TOnClickItem;
}

interface ICheckboxSection {
  items?: string[];
  title: string;
  subtitle?: string;
  subsections?: ICheckboxSubsection[];
  onClickItem: TOnClickItem;
  className?: string;
}

const CheckboxSectionItem = ({
  text,
  onClickItem,
  idx,
}: ICheckboxSectionItem): JSX.Element => {
  const handleOnToggle = useCallback(
    (isChecked: boolean) => onClickItem(idx, isChecked),
    [idx, onClickItem],
  );
  return <Checkbox onToggle={handleOnToggle} text={text} />;
};

const CheckboxList = ({ items, onClickItem }: ICheckboxList): JSX.Element => {
  const itemComponents = useMemo(
    () =>
      items.map((text, idx) => (
        <CheckboxSectionItem
          key={text}
          text={text}
          idx={idx}
          onClickItem={onClickItem}
        />
      )),
    [items, onClickItem],
  );

  return (
    <div className="flex flex-wrap gap-y-6 gap-x-4 max-w-[1000px]">
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
      <h4 className="font-medium text-sm text-dimGray mb-2 mt-6">{title}</h4>
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
      <h3 className="font-semibold text-xl text-dimGray mb-2">{title}</h3>
      <h4 className="text-sm text-dimGray mb-6">{subtitle}</h4>
      {items && <CheckboxList items={items} onClickItem={onClickItem} />}
      {subsectionComponents}
    </div>
  );
};

export default CheckboxSection;
