import type { ReactElement } from 'react';

import { FormattedMessage } from 'react-intl';

import { Table, TableHead, TableHeader, TableRow } from '../ui/table';

interface IBaseTable {
  headers: string[];
  body: ReactElement;
}

const BaseTable = ({ headers, body }: IBaseTable): JSX.Element => {
  return (
    <div>
      <Table className="rounded-lg text-black bg-white w-full">
        <TableHeader className="bg-mediumGray">
          <TableRow>
            {headers.map(column => (
              <TableHead className="text-black border-b" key={column}>
                <FormattedMessage id={column} />
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
