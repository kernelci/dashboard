import { FormattedMessage } from "react-intl";

import { MdArrowBackIos, MdArrowForwardIos, MdExpandMore } from "react-icons/md";

import { useCallback, useEffect, useMemo, useState } from "react";

import TreeTable from "../Table/TreeTable";
import { Button } from "../ui/button";
import { Tree, TreeTableBody } from "../../types/tree/Tree";
import { useTreeTable } from "../../api/Tree";


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
    <div className="flex flex-row gap-4 text-sm text-black">
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
        <Button variant="outline" onClick={onClickBack} disabled={startIndex === 1}>
          <MdArrowBackIos className={buttonsClassName}/>    
        </Button>
        <Button variant="outline" onClick={onClickForward} disabled={endIndex === totalTrees}>
          <MdArrowForwardIos className={buttonsClassName}/>
        </Button>
      </div>
    </div>
  );
};

const FilterButton = (): JSX.Element => {
  return(
    <Button variant="outline" className="rounded-full w-[128px] border-black">
      <div className="flex flex-row gap-1 items-center">
        <FormattedMessage id="global.filters" />
        <MdExpandMore />
      </div>
    </Button>
  );
};

const TreeListingPage = (): JSX.Element => {

  const { data } = useTreeTable();

  const listItems: TreeTableBody[] = useMemo(() => {
    return data ? (data as Tree[]).map(tree => ({
      name: tree.tree_name ?? '',
      branch: tree.git_repository_branch ?? '',
      commit: tree.git_commit_hash ?? tree.patchset_hash ?? '',
      buildStatus: `${tree.build_status.valid} / ${tree.build_status.total}`,
      testStatus: `${tree.test_status.fail} / ${tree.test_status.total}`,
    })) : [];
  }, [data]);

  const itemsPerPage = 10;
  const [startIndex, setStartIndex] = useState(0);
  const [endIndex, setEndIndex] = useState(0);

  useEffect(() => {
    setEndIndex(listItems.length > itemsPerPage ? itemsPerPage : listItems.length);
  }, [listItems]);

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
      <FilterButton />
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

export default TreeListingPage;
