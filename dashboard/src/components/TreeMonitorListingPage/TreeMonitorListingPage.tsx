import { FormattedMessage } from "react-intl";

import { MdArrowBackIos, MdArrowForwardIos, MdExpandMore } from "react-icons/md";

import { useCallback, useState } from "react";

import TreeTable, { ITreeTableBody } from "../Table/TreeTable";
import { Button } from "../ui/button";


interface ITableInformation {
  startIndex: number;
  endIndex: number;
  totalTrees: number;
  itemsPerPage: number;
  onClickForward: () => void;
  onClickBack: () => void; 
}

const TableInfo = ({
  startIndex,
  endIndex,
  totalTrees,
  itemsPerPage,
  onClickForward,
  onClickBack,
}: ITableInformation): JSX.Element => {
  const buttonsClassName = "text-lightBlue font-bold"
  const groupsClassName = "flex flex-row items-center gap-2"
  return (
    <div className="flex flex-row gap-4 text-sm">
      <div className={groupsClassName}>
        <FormattedMessage id="table.showing"/>
        <span className="font-bold">{startIndex} - {endIndex}</span>
        <FormattedMessage id="table.of"/>
        <span className="font-bold">{totalTrees}</span>
        <FormattedMessage id="table.tree"/>
      </div>
      <div className={groupsClassName}>
        <FormattedMessage id="table.itemsPerPage"/>
        <span className="font-bold">{itemsPerPage}</span>
        <MdExpandMore className={buttonsClassName}/>
      </div>
      <div className="flex flex-row gap-2 items-center">
        <Button variant="outline" onClick={onClickBack}>
          <MdArrowBackIos className={buttonsClassName}/>    
        </Button>
        <Button variant="outline" onClick={onClickForward}>
          <MdArrowForwardIos className={buttonsClassName}/>
        </Button>
      </div>
    </div>
  );
};

const TreeMonitorListingPage = (): JSX.Element => {
  const listItems = treeTableRows;
  const itemsPerPage = 10;
  const [startIndex, setStartIndex] = useState(0);
  const [endIndex, setEndIndex] = useState(listItems.length+1 > itemsPerPage ? itemsPerPage : listItems.length+1);

  const onClickGoForward = useCallback(() => {
    setStartIndex(endIndex);
    setEndIndex(endIndex+itemsPerPage >= listItems.length ? listItems.length : endIndex+itemsPerPage)
  }, [endIndex, listItems]);

  const onClickGoBack = useCallback(() => {
    setStartIndex(startIndex-itemsPerPage);
    setEndIndex(endIndex % itemsPerPage !== 0 ? endIndex - endIndex % itemsPerPage : endIndex - itemsPerPage);
  }, [startIndex, endIndex]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-end gap-4">
      <Button variant="outline" className="rounded-full w-[128px] border-black">
        <div className="flex flex-row gap-1 items-center">
          <FormattedMessage id="global.filters" />
          <MdExpandMore />
        </div>
      </Button>
      <TableInfo 
        startIndex={startIndex+1}
        endIndex={endIndex}
        totalTrees={listItems.length}
        itemsPerPage={itemsPerPage}
        onClickBack={onClickGoBack}
        onClickForward={onClickGoForward}
      />
      </div>
      <TreeTable treeTableRows={listItems.slice(startIndex, endIndex)}/>
      <div className="flex flex-col items-end">
      <TableInfo
        startIndex={startIndex+1}
        endIndex={endIndex}
        totalTrees={listItems.length}
        itemsPerPage={itemsPerPage}
        onClickBack={onClickGoBack}
        onClickForward={onClickGoForward}
      />
      </div>
    </div>
  );
};

const treeTableRows: ITreeTableBody[] = [
    {
      name: "stable-rc1",
      branch: "linux-5.15",
      commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
      buildStatus: "150 completed",
      testStatus: "80 completed"
    },
    {
      name: "stable-rc2",
      branch: "linux-5.15",
      commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
      buildStatus: "10 completed",
      testStatus: "150 completed"
    },
    {
      name: "stable-rc3",
      branch: "linux-5.15",
      commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
      buildStatus: "10 completed",
      testStatus: "150 completed"
    },
    {
      name: "stable-rc4",
      branch: "linux-5.15",
      commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
      buildStatus: "10 completed",
      testStatus: "150 completed"
    },
    {
      name: "stable-rc5",
      branch: "linux-5.15",
      commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
      buildStatus: "10 completed",
      testStatus: "150 completed"
    },
    {
        name: "stable-rc6",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "150 completed",
        testStatus: "80 completed"
      },
      {
        name: "stable-rc7",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "10 completed",
        testStatus: "150 completed"
      },
      {
        name: "stable-rc8",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "10 completed",
        testStatus: "150 completed"
      },
      {
        name: "stable-rc9",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "10 completed",
        testStatus: "150 completed"
      },
      {
        name: "stable-rc10",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "10 completed",
        testStatus: "150 completed"
      },
      {
        name: "stable-rc11",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "10 completed",
        testStatus: "150 completed"
      },
      {
        name: "stable-rc12",
        branch: "linux-5.15",
        commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
        buildStatus: "10 completed",
        testStatus: "150 completed"
      }
  ];

export default TreeMonitorListingPage;
