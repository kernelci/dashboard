import type { ReactElement } from 'react';

import classNames from 'classnames';

import { Table, TableHead, TableHeader, TableRow } from '../ui/table';

interface IBaseTableCommon {
  headers: ReactElement[];
  className?: string;
}

interface IBodyTable extends IBaseTableCommon {
  body: React.ReactNode;
  children?: never;
}

interface IChildrenTable extends IBaseTableCommon {
  body?: never;
  children: React.ReactNode;
}

type TBaseTable = IBodyTable | IChildrenTable;

const BaseTable = ({
  headers,
  body,
  children,
  className,
}: TBaseTable): JSX.Element => {
  return (
    <div className="h-full">
      <Table
        className={classNames(
          className,
          'w-full rounded-lg bg-white text-black',
        )}
      >
        <TableHeader className="bg-mediumGray">
          <TableRow>
            {headers.map(column => (
              <TableHead className="border-b text-black" key={column.key}>
                {column}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        {body || children}
      </Table>
    </div>
  );
};

export default BaseTable;
