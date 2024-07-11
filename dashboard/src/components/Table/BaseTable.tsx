import type { ReactElement } from 'react';

import classNames from 'classnames';

import { Table, TableHead, TableHeader, TableRow } from '../ui/table';

interface IBaseTable {
  headers: ReactElement[];
  body: ReactElement;
  className?: string;
}

const BaseTable = ({ headers, body, className }: IBaseTable): JSX.Element => {
  return (
    <div className="h-full">
      <Table
        className={classNames(
          className,
          'rounded-lg text-black bg-white w-full',
        )}
      >
        <TableHeader className="bg-mediumGray">
          <TableRow>
            {headers.map(column => (
              <TableHead className="text-black border-b" key={column.key}>
                {column}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        {body}
      </Table>
    </div>
  );
};

export default BaseTable;
