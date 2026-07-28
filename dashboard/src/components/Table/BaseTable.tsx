import type { ComponentProps, ReactElement, ReactNode, JSX, Ref } from 'react';

import classNames from 'classnames';

import {
  Table,
  TableHead as TableHeadComponent,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface IBaseTableCommon {
  className?: string;
  containerClassName?: string;
  containerRef?: Ref<HTMLDivElement>;
  containerStyle?: ComponentProps<typeof Table>['containerStyle'];
  style?: ComponentProps<typeof Table>['style'];
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
  containerClassName,
  containerRef,
  containerStyle,
  style,
}: {
  children: ReactNode;
  className?: string;
  containerClassName?: string;
  containerRef?: Ref<HTMLDivElement>;
  containerStyle?: ComponentProps<typeof Table>['containerStyle'];
  style?: ComponentProps<typeof Table>['style'];
}): JSX.Element => {
  return (
    <Table
      className={classNames(className, 'rounded-lg bg-white text-black')}
      containerClassName={containerClassName}
      containerRef={containerRef}
      containerStyle={containerStyle}
      style={style}
    >
      {children}
    </Table>
  );
};

export const DumbTableHeader = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}): JSX.Element => {
  return (
    <TableHeader className={classNames('bg-medium-gray', className)}>
      <TableRow>{children}</TableRow>
    </TableHeader>
  );
};

export const TableHead = ({
  children,
  className,
  style,
  ...props
}: ComponentProps<typeof TableHeadComponent>): JSX.Element => {
  return (
    <TableHeadComponent
      className={classNames(
        className,
        'relative border-b font-bold text-black',
      )}
      style={style}
      {...props}
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
  containerClassName,
  containerRef,
  containerStyle,
  style,
}: TBaseTable): JSX.Element => {
  return (
    <div className="h-full">
      <DumbBaseTable
        className={className}
        containerClassName={containerClassName}
        containerRef={containerRef}
        containerStyle={containerStyle}
        style={style}
      >
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
