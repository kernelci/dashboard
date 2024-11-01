import { FormattedMessage } from 'react-intl';

import { memo, useMemo } from 'react';

import BaseCard from '@/components/Cards/BaseCard';
import { GroupedTestStatus } from '@/components/Status/Status';

import type { ISummaryTable } from '@/components/Summary/Summary';
import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import type { TFilterObjectsKeys } from '@/types/tree/TreeDetails';

interface IErrorsSummaryBuild extends Pick<ISummaryTable, 'summaryBody'> {
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}

const ErrorsSummaryBuild = ({
  summaryBody,
  toggleFilterBySection,
}: IErrorsSummaryBuild): JSX.Element => {
  const summaryHeaders = useMemo(
    () => [
      <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
      <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
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
              <SummaryItem
                key={row.arch.text}
                arch={{ text: row.arch.text }}
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
