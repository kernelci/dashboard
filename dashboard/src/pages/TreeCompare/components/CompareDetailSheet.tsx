import { type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import { FormattedMessage } from 'react-intl';

import { Sheet } from '@/components/Sheet';
import { WrapperSheetContent } from '@/components/Sheet/WrapperSheetContent';
import { LogSheetPanel } from '@/components/Log/LogSheetPanel';
import { MemoizedMoreDetailsButton } from '@/components/Button/MoreDetailsButton';
import { useLogData, type LogData, type LogType } from '@/hooks/useLogData';
import type {
  CompareFailureRow,
  CompareItemStatus,
} from '@/types/tree/TreeCompare';

import { CompareChangeBadge, CompareStatusChip } from './CompareChangeDisplay';

export type CompareDetailItem = {
  title: string;
  subtitle: string;
  change: CompareFailureRow['change'];
  sideA: CompareItemStatus;
  sideB: CompareItemStatus;
  idA: string | null;
  idB: string | null;
};

export function compareRowToDetailItem(
  row: CompareFailureRow,
): CompareDetailItem {
  const shared = {
    change: row.change,
    sideA: row.sideA,
    sideB: row.sideB,
    idA: row.idA,
    idB: row.idB,
  };
  if ('path' in row) {
    return {
      ...shared,
      title: row.path,
      subtitle: `${row.hardware} · ${row.arch}`,
    };
  }
  return {
    ...shared,
    title: row.config,
    subtitle: `${row.arch} · ${row.compiler}`,
  };
}

function detailsLink(logType: LogType, id: string): LinkProps {
  if (logType === 'build') {
    return { to: '/build/$buildId', params: { buildId: id } };
  }
  return { to: '/test/$testId', params: { testId: id } };
}

function SideColumn({
  labelId,
  status,
  id,
  logType,
  logData,
  isLoading,
}: {
  labelId: 'treeCompare.sideA' | 'treeCompare.sideB';
  status: CompareItemStatus;
  id: string | null;
  logType: LogType;
  logData: LogData;
  isLoading: boolean;
}): JSX.Element {
  return (
    <section className="flex min-w-0 flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-dim-black text-sm font-semibold">
            <FormattedMessage id={labelId} />
          </h3>
          <CompareStatusChip status={status} />
        </div>
        {id && (
          <MemoizedMoreDetailsButton linkProps={detailsLink(logType, id)} />
        )}
      </div>
      {id ? (
        <div className="flex flex-col gap-2">
          <LogSheetPanel
            logData={logData}
            isLoading={isLoading}
            variant="compare"
          />
        </div>
      ) : (
        <p className="text-dim-gray text-sm">
          <FormattedMessage id="treeCompare.detail.missingSide" />
        </p>
      )}
    </section>
  );
}

interface CompareDetailSheetProps {
  open: boolean;
  item: CompareDetailItem | null;
  logType: LogType;
  onOpenChange: (open: boolean) => void;
  onPrevious: () => void;
  onNext: () => void;
  hasPrevious: boolean;
  hasNext: boolean;
}

export function CompareDetailSheet({
  open,
  item,
  logType,
  onOpenChange,
  onPrevious,
  onNext,
  hasPrevious,
  hasNext,
}: CompareDetailSheetProps): JSX.Element {
  const logA = useLogData(item?.idA ?? '', item?.idA ? logType : undefined);
  const logB = useLogData(item?.idB ?? '', item?.idB ? logType : undefined);
  const isLoading = logA.isLoading || logB.isLoading;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <WrapperSheetContent
        sheetTitle="logSheet.title"
        navigationLogsActions={{
          previousItem: onPrevious,
          nextItem: onNext,
          hasPrevious,
          hasNext,
          isLoading,
        }}
      >
        {item && (
          <div className="flex flex-col gap-4">
            <div className="bg-light-gray flex flex-col gap-2.5 rounded-lg border border-gray-200 p-3">
              <p className="text-dim-black text-sm font-semibold">
                {item.title}
              </p>
              <p className="text-dim-gray text-xs">{item.subtitle}</p>
              <div className="flex flex-wrap items-center gap-2">
                <CompareStatusChip status={item.sideA} />
                <span className="text-dim-gray text-sm">→</span>
                <CompareStatusChip status={item.sideB} />
                <CompareChangeBadge change={item.change} />
              </div>
            </div>
            <div className="grid gap-6 lg:grid-cols-2">
              <SideColumn
                labelId="treeCompare.sideA"
                status={item.sideA}
                id={item.idA}
                logType={logType}
                logData={logA.data}
                isLoading={logA.isLoading}
              />
              <SideColumn
                labelId="treeCompare.sideB"
                status={item.sideB}
                id={item.idB}
                logType={logType}
                logData={logB.data}
                isLoading={logB.isLoading}
              />
            </div>
          </div>
        )}
      </WrapperSheetContent>
    </Sheet>
  );
}
