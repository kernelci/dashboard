import cls from 'classnames';

import { useCallback, useMemo, type JSX } from 'react';

import type { MessageDescriptor } from 'react-intl';

import type { TFilterObjectsKeys } from '@/types/general';

import Checkbox from '@/components/Checkbox/Checkbox';

import { FilterTypeIcon } from './Drawer';

type TOnClickItem = (value: string) => void;

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
  isGlobal?: boolean;
  subtitle?: string;
  subsections?: ICheckboxSubsection[];
  onClickItem: TOnClickItem;
  className?: string;
}

export interface ISectionItem {
  title: MessageDescriptor['id'];
  subtitle: MessageDescriptor['id'];
  sectionKey: TFilterObjectsKeys;
  isGlobal?: boolean;
}

type SplitFilterString = `${string}__${string}`;

const extractCheckboxValue = (value: SplitFilterString | undefined): string => {
  if (!value) {
    return '';
  }

  const valueSplit = value.split('__');
  return valueSplit[0];
};

const CheckboxSectionItem = ({
  value,
  onClickItem,
  isSelected,
}: ICheckboxSectionItem): JSX.Element => {
  const handleOnToggle = useCallback(
    () => onClickItem(value),
    [value, onClickItem],
  );
  return (
    <Checkbox
      onToggle={handleOnToggle}
      text={extractCheckboxValue(value as SplitFilterString)}
      isChecked={isSelected}
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
      <h4 className="text-dim-gray mt-6 mb-2 text-sm font-medium">{title}</h4>
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
  isGlobal = false,
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
      <h3 className="text-dim-gray mb-2 flex items-center gap-[0.4rem] text-xl font-semibold">
        <FilterTypeIcon type={isGlobal ? 'global' : 'tab'} />
        <span>{title}</span>
      </h3>
      <h4 className="text-dim-gray mb-6 text-sm">{subtitle}</h4>
      {items && <CheckboxList items={items} onClickItem={onClickItem} />}
      {subsectionComponents}
    </div>
  );
};

export default CheckboxSection;
