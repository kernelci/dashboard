import { FormattedMessage } from 'react-intl';

import { memo, useMemo } from 'react';

import BaseCard from '@/components/Cards/BaseCard';
import { GroupedTestStatus } from '@/components/Status/Status';

import type { ISummaryTable } from '../Summary';
import { DumbSummary, MemoizedSummaryItem } from '../Summary';

interface IErrorsSummaryBuild<T> extends Pick<ISummaryTable, 'summaryBody'> {
  toggleFilterBySection: (value: string, filterSection: T) => void;
  diffFilter: Record<string, Record<string, boolean>>;
}

const ErrorsSummaryBuild = <T,>({
  summaryBody,
  toggleFilterBySection,
  diffFilter,
}: IErrorsSummaryBuild<T>): JSX.Element => {
  const summaryHeaders = useMemo(
    () => [
      <FormattedMessage key="global.arch" id="global.arch" />,
      <FormattedMessage key="global.compiler" id="global.compiler" />,
    ],
    [],
  );

  return (
    <BaseCard
      title="Summary"
      content={
        <DumbSummary summaryHeaders={summaryHeaders}>
          {summaryBody?.map(row => {
            return (
              <MemoizedSummaryItem
                key={row.arch.text}
                arch={{ text: row.arch.text }}
                diffFilter={diffFilter}
                onClickCompiler={value =>
                  toggleFilterBySection(value, 'compilers' as T)
                }
                onClickKey={value => toggleFilterBySection(value, 'archs' as T)}
                leftIcon={
                  <GroupedTestStatus
                    forceNumber={false}
                    fail={row.arch.errors}
                    error={row.arch.unknown}
                    pass={row.arch.success}
                  />
                }
                compilers={row.compilers}
              />
            );
          })}
        </DumbSummary>
      }
    />
  );
};

export const MemoizedErrorsSummaryBuild = memo(ErrorsSummaryBuild) as <T>(
  props: IErrorsSummaryBuild<T>,
) => JSX.Element;
