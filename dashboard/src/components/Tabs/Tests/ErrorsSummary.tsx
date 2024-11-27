import { memo } from 'react';
import { FormattedMessage } from 'react-intl';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import { GroupedTestStatus } from '@/components/Status/Status';

import type { ArchCompilerStatus, TFilter } from '@/types/general';

import { DumbSummary, MemoizedSummaryItem } from '@/components/Tabs/Summary';

interface IErrorsSummary {
  archCompilerErrors: ArchCompilerStatus[];
  title: IBaseCard['title'];
  diffFilter: TFilter;
  disabled?: boolean;
}

const summaryHeaders = [
  <FormattedMessage key="global.arch" id="global.arch" />,
  <FormattedMessage key="global.compiler" id="global.compiler" />,
];

const ErrorsSummary = ({
  archCompilerErrors,
  title,
  disabled,
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
                disabled={disabled}
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
