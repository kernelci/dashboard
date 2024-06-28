import { useMemo } from "react";

import { TableRow, TableCell } from "../ui/table";

import BaseTable from "./BaseTable";

interface ITreeTableBody {
  name: string;
  branch: string;
  commit: string;
  buildStatus: string;
  testStatus: string;
}

const treeTableColumnsLabelId = [
  'treeTable.tree',
  'treeTable.branch',
  'treeTable.commit',
  'treeTable.build',
  'treeTable.test'
];

const treeTableRows: ITreeTableBody[] = [
  {
    name: "stable-rc",
    branch: "linux-5.15",
    commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
    buildStatus: "150 completed",
    testStatus: "80 completed"
  },
  {
    name: "stable-rc",
    branch: "linux-5.15",
    commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
    buildStatus: "10 completed",
    testStatus: "150 completed"
  },
  {
    name: "stable-rc",
    branch: "linux-5.15",
    commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
    buildStatus: "10 completed",
    testStatus: "150 completed"
  },
  {
    name: "stable-rc",
    branch: "linux-5.15",
    commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
    buildStatus: "10 completed",
    testStatus: "150 completed"
  },
  {
    name: "stable-rc",
    branch: "linux-5.15",
    commit: "asidnasidn-oqiwejeoij-oaidnosdnk",
    buildStatus: "10 completed",
    testStatus: "150 completed"
  }
];

const TreeTableRow = (row: ITreeTableBody): JSX.Element => {
  return (
    <TableRow>
      <TableCell>{row.name}</TableCell>
      <TableCell>{row.branch}</TableCell>
      <TableCell>{row.commit}</TableCell>
      <TableCell><div className="bg-lightGray w-fit h-fit p-1 rounded-lg">{row.buildStatus}</div></TableCell>
      <TableCell><div className="bg-lightGray w-fit h-fit p-1 rounded-lg">{row.testStatus}</div></TableCell>
    </TableRow>
  );
};

const TreeTable = () : JSX.Element => {
  const treeTableBody = useMemo(() => {
    return (
      treeTableRows.map((row: ITreeTableBody) => (
        <TreeTableRow 
          key={row.commit} 
          name={row.name}
          branch={row.branch}
          commit={row.commit}
          buildStatus={row.buildStatus}
          testStatus={row.testStatus}/>
      ))
    );
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [treeTableRows]);

  return(
    <BaseTable headers={treeTableColumnsLabelId} body={<>{treeTableBody}</>} />
  );
}

export default TreeTable;
