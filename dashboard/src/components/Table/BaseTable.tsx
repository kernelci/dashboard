import type { ComponentProps, ReactElement, ReactNode } from 'react';

import classNames from 'classnames';

import {
  Table,
  TableHead as TableHeadComponent,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface IBaseTableCommon {
  className?: string;
}

interface IBodyTable {
  body: React.ReactNode;
  children?: never;
}

interface IChildrenTable {
  body?: never;
  children: React.ReactNode;
}

interface IHeaderTable {
  headers: ReactElement[];
  headerComponents?: never;
}

interface IHeaderComponentsTable {
  headers?: never;
  headerComponents: JSX.Element[];
}

type TBaseTable = (IBodyTable | IChildrenTable) &
  (IHeaderTable | IHeaderComponentsTable) &
  IBaseTableCommon;

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
    <TableHeader className="bg-medium-gray">
      <TableRow>{children}</TableRow>
    </TableHeader>
  );
};

export const TableHead = ({
  children,
  className,
}: ComponentProps<typeof TableHeadComponent>): JSX.Element => {
  return (
    <TableHeadComponent
      className={classNames(className, 'border-b font-bold text-black')}
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
