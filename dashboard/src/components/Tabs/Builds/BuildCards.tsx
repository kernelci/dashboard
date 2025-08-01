import { FormattedMessage } from 'react-intl';

import { memo, useMemo, type JSX } from 'react';

import BaseCard from '@/components/Cards/BaseCard';
import { GroupedTestStatus } from '@/components/Status/Status';

import type { ISummaryTable } from '@/components/Tabs/Summary';
import { DumbSummary, MemoizedSummaryItem } from '@/components/Tabs/Summary';
import type { TFilter, TFilterObjectsKeys } from '@/types/general';

interface IErrorsSummaryBuild extends Pick<ISummaryTable, 'summaryBody'> {
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
  diffFilter: TFilter;
}

const ErrorsSummaryBuild = ({
  summaryBody,
  toggleFilterBySection,
  diffFilter,
}: IErrorsSummaryBuild): JSX.Element => {
  const sortedSummaryBody = useMemo(
    () =>
      summaryBody.sort((a, b) => {
        const errorsA = a.arch.errors ?? 0;
        const errorsB = b.arch.errors ?? 0;

        if (errorsB !== errorsA) {
          return errorsB - errorsA;
        }

        return a.arch.text.localeCompare(b.arch.text);
      }),
    [summaryBody],
  );

  const summaryHeaders = useMemo(
    () => [
      <FormattedMessage key="global.arch" id="global.arch" />,
      <FormattedMessage key="global.compiler" id="global.compiler" />,
    ],
    [],
  );

  return (
    <BaseCard
      title={<FormattedMessage id="global.summary" />}
      content={
        <DumbSummary summaryHeaders={summaryHeaders}>
          {sortedSummaryBody?.map(row => {
            return (
              <MemoizedSummaryItem
                key={row.arch.text}
                arch={{ text: row.arch.text }}
                diffFilter={diffFilter}
                onClickCompiler={value =>
                  toggleFilterBySection(value, 'compilers')
                }
                onClickKey={value => toggleFilterBySection(value, 'archs')}
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

export const MemoizedErrorsSummaryBuild = memo(ErrorsSummaryBuild);
