import { memo } from 'react';
import { FormattedMessage } from 'react-intl';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { GroupedTestStatus } from '@/components/Status/Status';

import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import type { ArchCompilerStatus } from '@/types/general';

interface IErrorsSummary {
  archCompilerErrors: ArchCompilerStatus[];
  title: IBaseCard['title'];
}

const summaryHeaders = [
  <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
  <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
];

const ErrorsSummary = ({
  archCompilerErrors,
  title,
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
              <SummaryItem
                key={e.arch}
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

export default memo(ErrorsSummary);
