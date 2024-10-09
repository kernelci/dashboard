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
  className?: string;
  gridClassName?: string;
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
  gridClassName,
}: {
  children: ReactNode;
  gridClassName?: string;
}): JSX.Element => {
  return (
    <TableHeader className="bg-mediumGray">
      <TableRow className={gridClassName}>{children}</TableRow>
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
  body,
  children,
  className,
  gridClassName,
}: TBaseTable): JSX.Element => {
  return (
    <div className="h-full">
      <DumbBaseTable className={className}>
        <DumbTableHeader gridClassName={gridClassName}>
          {headers.map(column => (
            <TableHead
              className={gridClassName ? 'flex items-center' : ''}
              /*className={`flex flex-col justify-center w-[${fieldSizes[index]}%]`}*/ key={
                column.key
              }
            >
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
