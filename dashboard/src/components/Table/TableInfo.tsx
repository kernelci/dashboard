import { MdArrowBackIos, MdArrowForwardIos } from 'react-icons/md';
import { FormattedMessage } from 'react-intl';

import { useCallback, useMemo } from 'react';

import { MessagesKey } from '@/locales/messages';

import {
  Select,
  SelectItem,
  SelectContent,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { Button } from '../ui/button';

interface IItemsPerPageSelector {
  onValueChange: (value: number) => void;
  values: number[];
  selected: number;
}

const ItemsPerPageSelector = ({
  onValueChange,
  values,
  selected,
}: IItemsPerPageSelector): JSX.Element => {
  const onChangeHandle = useCallback(
    (v: string) => onValueChange(parseInt(v)),
    [onValueChange],
  );

  const selectItems = useMemo(
    () =>
      values.map(v => (
        <SelectItem key={v} value={v.toString()}>
          {v}
        </SelectItem>
      )),
    [values],
  );

  return (
    <div className="flex flex-row items-center gap-2">
      <FormattedMessage id="table.itemsPerPage" />
      <Select value={selected.toString()} onValueChange={onChangeHandle}>
        <SelectTrigger className="w-16">
          <SelectValue placeholder="" />
        </SelectTrigger>
        <SelectContent>{selectItems}</SelectContent>
      </Select>
    </div>
  );
};

interface ITableInformation {
  itemName: MessagesKey;
  startIndex: number;
  endIndex: number;
  totalTrees: number;
  itemsPerPageValues: number[];
  itemsPerPageSelected: number;
  onChangeItemsPerPage: (value: number) => void;
  onClickForward: () => void;
  onClickBack: () => void;
}

export const TableInfo = ({
  itemName,
  startIndex,
  endIndex,
  totalTrees,
  itemsPerPageValues,
  itemsPerPageSelected,
  onChangeItemsPerPage,
  onClickForward,
  onClickBack,
}: ITableInformation): JSX.Element => {
  const buttonsClassName = 'text-blue font-bold';
  const groupsClassName = 'flex flex-row items-center gap-2';
  return (
    <div className="flex flex-row gap-4 text-sm text-black">
      <div className={groupsClassName}>
        <FormattedMessage id="table.showing" />
        <span className="font-bold">
          {startIndex} - {endIndex}
        </span>
        <FormattedMessage id="table.of" />
        <span className="font-bold">{totalTrees}</span>
        <FormattedMessage id={itemName} />
      </div>
      <ItemsPerPageSelector
        onValueChange={onChangeItemsPerPage}
        values={itemsPerPageValues}
        selected={itemsPerPageSelected}
      />
      <div className="flex flex-row items-center gap-2">
        <Button
          variant="outline"
          onClick={onClickBack}
          disabled={startIndex === 1}
        >
          <MdArrowBackIos className={buttonsClassName} />
        </Button>
        <Button
          variant="outline"
          onClick={onClickForward}
          disabled={endIndex === totalTrees}
        >
          <MdArrowForwardIos className={buttonsClassName} />
        </Button>
      </div>
    </div>
  );
};
