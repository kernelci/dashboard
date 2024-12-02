import { FormattedMessage } from 'react-intl';

import { memo, useMemo } from 'react';

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
