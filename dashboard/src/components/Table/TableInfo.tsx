import {
  MdExpandMore,
  MdArrowBackIos,
  MdArrowForwardIos,
} from 'react-icons/md';
import { FormattedMessage } from 'react-intl';

import { Button } from '../ui/button';

interface ITableInformation {
  startIndex: number;
  endIndex: number;
  totalTrees: number;
  itemsPerPage: number;
  onClickForward: () => void;
  onClickBack: () => void;
}

export const TableInfo = ({
  startIndex,
  endIndex,
  totalTrees,
  itemsPerPage,
  onClickForward,
  onClickBack,
}: ITableInformation): JSX.Element => {
  const buttonsClassName = 'text-lightBlue font-bold';
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
        <FormattedMessage id="table.tree" />
      </div>
      <div className={groupsClassName}>
        <FormattedMessage id="table.itemsPerPage" />
        <span className="font-bold">{itemsPerPage}</span>
        <MdExpandMore className={buttonsClassName} />
      </div>
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
