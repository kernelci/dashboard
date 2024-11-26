import { memo } from 'react';
import { FormattedMessage } from 'react-intl';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { GroupedTestStatus } from '@/components/Status/Status';

import type { ArchCompilerStatus } from '@/types/general';

import { DumbSummary, MemoizedSummaryItem } from '../Summary';

interface IErrorsSummary {
  archCompilerErrors: ArchCompilerStatus[];
  title: IBaseCard['title'];
  diffFilter: Record<string, Record<string, boolean>>;
}

const summaryHeaders = [
  <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
  <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
];

const ErrorsSummary = ({
  archCompilerErrors,
  title,
  diffFilter,
}: IErrorsSummary): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbSummary summaryHeaders={summaryHeaders}>
          {archCompilerErrors.map(e => {
            const statusCounts = e.status;
            const currentCompilers = [e.compiler];
            return (
              <MemoizedSummaryItem
                key={e.arch}
                diffFilter={diffFilter}
                arch={{
                  text: e.arch,
                }}
                leftIcon={
                  <GroupedTestStatus
                    forceNumber={false}
                    done={statusCounts.DONE}
                    fail={statusCounts.FAIL}
                    error={statusCounts.ERROR}
                    miss={statusCounts.MISS}
                    pass={statusCounts.PASS}
                    skip={statusCounts.SKIP}
                    nullStatus={statusCounts.NULL}
                  />
                }
                compilers={currentCompilers}
              />
            );
          })}
        </DumbSummary>
      }
    />
  );
};

const MemoizedErrorsSummary = memo(ErrorsSummary);

export default MemoizedErrorsSummary;
