import type { ComponentProps, ReactElement, ReactNode } from 'react';

import classNames from 'classnames';

import {
  Table,
  TableHead as TableHeadComponent,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface IBaseTableCommon {
  headers: ReactElement[];
  headerComponents?: JSX.Element[];
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

export const DumbBaseTable = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}): JSX.Element => {
  return (
    <Table
      className={classNames(className, 'w-full rounded-lg bg-white text-black')}
    >
      {children}
    </Table>
  );
};

export const DumbTableHeader = ({
  children,
}: {
  children: ReactNode;
}): JSX.Element => {
  return (
    <TableHeader className="bg-mediumGray">
      <TableRow>{children}</TableRow>
    </TableHeader>
  );
};

export const TableHead = ({
  children,
  onClick,
}: ComponentProps<typeof TableHeadComponent>): JSX.Element => {
  return (
    <TableHeadComponent
      className="border-b font-bold text-black"
      onClick={onClick}
    >
      {children}
    </TableHeadComponent>
  );
};

const BaseTable = ({
  headers,
  headerComponents,
  body,
  children,
  className,
}: TBaseTable): JSX.Element => {
  return (
    <div className="h-full">
      <DumbBaseTable className={className}>
        <DumbTableHeader>
          {headerComponents ??
            headers.map(column => (
              <TableHead className="border-b text-black" key={column.key}>
                {column}
              </TableHead>
            ))}
        </DumbTableHeader>
        {body || children}
      </DumbBaseTable>
    </div>
  );
};

export default BaseTable;
