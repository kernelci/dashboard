import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { RiProhibited2Line } from 'react-icons/ri';

import { Separator } from '@/components/ui/separator';

import BaseTable from '@/components/Table/BaseTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCell, TableRow } from '@/components/ui/table';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { useBuildTests } from '@/api/buildTests';
import { usePagination } from '@/hooks/usePagination';
import { formatDate } from '@/utils/utils';
import { MessagesKey } from '@/locales/messages';

interface IBuildDetailsTestSection {
  buildId: string;
}

const headerLabelIds: MessagesKey[] = [
  'global.origins',
  'global.name',
  'buildDetails.testResults',
  'buildDetails.startTime',
];

const testCellProps = [
  {
    name: 'pass_tests',
    colorClass: 'bg-lightGreen',
    tooltipLabelId: 'global.pass',
  },
  {
    name: 'done_tests',
    colorClass: 'bg-green',
    tooltipLabelId: 'global.done',
  },
  {
    name: 'fail_tests',
    colorClass: 'bg-lightRed',
    tooltipLabelId: 'global.failed',
  },
  {
    name: 'error_tests',
    colorClass: 'bg-red',
    tooltipLabelId: 'global.error',
  },
  {
    name: 'miss_tests',
    colorClass: 'bg-yellow',
    tooltipLabelId: 'global.missed',
  },
  {
    name: 'skip_tests',
    colorClass: 'bg-darkGray',
    tooltipLabelId: 'global.skiped',
  },
  {
    name: 'total_tests',
    colorClass: 'bg-darkGray2',
    tooltipLabelId: 'global.total',
  },
] as const;

const ITEMS_PER_PAGE = 10;

const NoTestFound = (): JSX.Element => (
  <div className="flex flex-col items-center py-6 text-weakGray">
    <RiProhibited2Line className="h-14 w-14" />
    <h1 className="text-2xl font-semibold">
      <FormattedMessage id={'buildDetails.noTestResults'} />
    </h1>
  </div>
);

const BuildDetailsTestSection = ({
  buildId,
}: IBuildDetailsTestSection): JSX.Element => {
  const intl = useIntl();
  const [pathParam, setPathParam] = useState('');
  const { data, error } = useBuildTests(buildId, pathParam);
  const data_len = data?.length || 0;
  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE);

  const onClickName = useCallback(
    (e: React.MouseEvent<HTMLTableCellElement>) => {
      if (e.target instanceof HTMLTableCellElement) {
        setPathParam(e.target.innerText);
      }
    },
    [],
  );

  const headers = useMemo(() => {
    return headerLabelIds.map(labelId => (
      <FormattedMessage key={labelId} id={labelId} />
    ));
  }, []);

  const rows = useMemo(() => {
    if (!data || error) return <></>;

    return data.slice(startIndex, endIndex).map(test => (
      <TableRow key={test.current_path}>
        <TableCell>{test.origins.join(', ')}</TableCell>
        <TableCell onClick={onClickName}>{test.current_path}</TableCell>
        <TableCell className="flex flex-row gap-1">
          {testCellProps.map(props => (
            <ColoredCircle
              key={test[props.name]}
              tooltipText={intl.formatMessage({ id: props.tooltipLabelId })}
              quantity={test[props.name]}
              backgroundClassName={props.colorClass}
            />
          ))}
        </TableCell>
        <TableCell>{formatDate(test.start_time)}</TableCell>
      </TableRow>
    ));
  }, [data, error, intl, onClickName, startIndex, endIndex]);

  const tableInfoElement = (
    <div className="flex flex-col items-end">
      <TableInfo
        startIndex={startIndex + 1}
        endIndex={endIndex}
        totalTrees={data_len}
        itemsPerPage={ITEMS_PER_PAGE}
        onClickBack={onClickGoBack}
        onClickForward={onClickGoForward}
      />
    </div>
  );

  const hasTest = data && data.length > 0 && !error;
  return (
    <>
      <span className="text-2xl font-bold">
        {intl.formatMessage({ id: 'buildDetails.testResults' })}
      </span>
      <Separator className="my-6 bg-darkGray" />
      {hasTest ? (
        <div className="flex flex-col gap-6">
          {tableInfoElement}
          <BaseTable headers={headers}>{rows}</BaseTable>
          {tableInfoElement}
        </div>
      ) : (
        <NoTestFound />
      )}
    </>
  );
};

export default BuildDetailsTestSection;
