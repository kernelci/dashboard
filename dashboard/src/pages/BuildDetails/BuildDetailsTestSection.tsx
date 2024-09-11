import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { RiProhibited2Line } from 'react-icons/ri';

import { Separator } from '@/components/ui/separator';

import BaseTable from '@/components/Table/BaseTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCell, TableRow } from '@/components/ui/table';
import { useBuildTests } from '@/api/buildTests';
import { usePagination } from '@/hooks/usePagination';
import { MessagesKey } from '@/locales/messages';
import { TestStatus } from '@/components/Status/Status';

interface IBuildDetailsTestSection {
  buildId: string;
}

const headerLabelIds: MessagesKey[] = [
  'global.origins',
  'global.name',
  'buildDetails.testResults',
  'buildDetails.startTime',
];

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
      <TableRow key={test.path_group}>
        <TableCell onClick={onClickName}>{test.path_group}</TableCell>
        <TableCell className="flex flex-row gap-1">
          <TestStatus
            pass={test.pass_tests}
            done={test.done_tests}
            miss={test.miss_tests}
            fail={test.fail_tests}
            skip={test.skip_tests}
            error={test.error_tests}
          />
        </TableCell>
      </TableRow>
    ));
  }, [data, error, onClickName, startIndex, endIndex]);

  const tableInfoElement = (
    <div className="flex flex-col items-end">
      <TableInfo
        itemName="global.tests"
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
