import { FormattedMessage } from 'react-intl';
import { FaRegDotCircle, FaRegCircle } from 'react-icons/fa';
import { memo } from 'react';

import { Link } from '@tanstack/react-router';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import BaseCard, { IBaseCard } from '@/components/Cards/BaseCard';
import ListingItem, { ItemType } from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import { ArchCompilerStatus, TTreeTestsData } from '@/types/tree/TreeDetails';

import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import StatusChartMemoized, {
  Colors,
  StatusChartValues,
} from '@/components/StatusChart/StatusCharts';
import { groupStatus } from '@/utils/status';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { TIssue } from '@/types/general';
import { NoIssueFound } from '@/components/Issue/IssueSection';
import { ScrollArea } from '@/components/ui/scroll-area';

import FilterLink from '../TreeDetailsFilterLink';

interface IConfigList extends Pick<TTreeTestsData, 'configStatusCounts'> {
  title: IBaseCard['title'];
}

const ConfigsList = ({
  configStatusCounts,
  title,
}: IConfigList): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {Object.keys(configStatusCounts).map(configName => {
            const { DONE, FAIL, ERROR, MISS, PASS, SKIP } =
              configStatusCounts[configName];
            return (
              <FilterLink
                key={configName}
                filterSection="configs"
                filterValue={configName}
              >
                <ListingItem
                  hasBottomBorder
                  key={configName}
                  text={configName}
                  leftIcon={
                    <GroupedTestStatus
                      done={DONE}
                      fail={FAIL}
                      error={ERROR}
                      miss={MISS}
                      pass={PASS}
                      skip={SKIP}
                      forceNumber={false}
                    />
                  }
                />
              </FilterLink>
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
export const MemoizedConfigList = memo(ConfigsList);

interface IHardwareTested
  extends Pick<TTreeTestsData, 'environmentCompatible'> {
  title: IBaseCard['title'];
}

const HardwareTested = ({
  environmentCompatible,
  title,
}: IHardwareTested): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <ScrollArea className="h-[350px]">
          <DumbListingContent>
            {environmentCompatible &&
              Object.entries(environmentCompatible).map(
                ([hardwareTestedItem, hardwareTestedCount]) => {
                  return (
                    <ListingItem
                      hasBottomBorder
                      key={hardwareTestedItem}
                      errors={hardwareTestedCount}
                      text={hardwareTestedItem}
                      showNumber={true}
                    />
                  );
                },
              )}
          </DumbListingContent>
        </ScrollArea>
      }
    />
  );
};
export const MemoizedHardwareTested = memo(HardwareTested);

interface IErrorCountList extends Pick<TTreeTestsData, 'errorMessageCounts'> {
  title: IBaseCard['title'];
}

const ErrorCountList = ({
  errorMessageCounts,
  title,
}: IErrorCountList): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {Object.keys(errorMessageCounts).map(errorMessage => {
            const currentErrorMessageCount = errorMessageCounts[errorMessage];
            return (
              <ListingItem
                key={errorMessage}
                text={errorMessage}
                errors={currentErrorMessageCount}
              />
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
export const MemoizedErrorCountList = memo(ErrorCountList);

interface IErrorsSummary {
  archCompilerErrors: ArchCompilerStatus[];
  title: IBaseCard['title'];
}

const ErrorsSummary = ({
  archCompilerErrors,
  title,
}: IErrorsSummary): JSX.Element => {
  const summaryHeaders = [
    <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
    <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
  ];

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

export const MemoizedErrorsSummary = memo(ErrorsSummary);

interface IStatusChart extends Pick<TTreeTestsData, 'statusCounts'> {
  title: IBaseCard['title'];
}

const StatusChart = ({ statusCounts, title }: IStatusChart): JSX.Element => {
  const groupedStatusCounts = groupStatus({
    doneCount: statusCounts.DONE ?? 0,
    errorCount: statusCounts.ERROR ?? 0,
    failCount: statusCounts.FAIL ?? 0,
    missCount: statusCounts.MISS ?? 0,
    passCount: statusCounts.PASS ?? 0,
    skipCount: statusCounts.SKIP ?? 0,
  });

  const chartElements = [
    {
      label: 'bootsTab.success',
      value: groupedStatusCounts.successCount,
      color: Colors.Green,
    },
    {
      label: 'global.failed',
      value: groupedStatusCounts.failedCount,
      color: Colors.Red,
    },
    {
      label: 'global.inconclusive',
      value: groupedStatusCounts.inconclusiveCount ?? 0,
      color: Colors.Gray,
    },
  ] satisfies StatusChartValues[];

  const filteredChartElements = chartElements.filter(chartElement => {
    return chartElement.value > 0;
  });

  const totalCount = Object.values(statusCounts).reduce(
    (accumulator: number, count) => accumulator + (count ?? 0),
    0,
  );

  return (
    <BaseCard
      title={title}
      content={
        <StatusChartMemoized
          type="chart"
          elements={filteredChartElements}
          pieCentralLabel="Statuses"
          pieCentralDescription={<>{totalCount}</>}
        />
      }
    />
  );
};

export const MemoizedStatusChart = memo(StatusChart);

interface IIssuesList {
  issues: TIssue[];
  title: IBaseCard['title'];
}

const IssuesList = ({ issues, title }: IIssuesList): JSX.Element => {
  const hasIssue = issues.length > 0;

  const titleElement = (
    <span>
      {title}
      {hasIssue && (
        <ColoredCircle
          className="ml-2 font-normal"
          backgroundClassName={ItemType.Error}
          quantity={issues.length}
        />
      )}
    </span>
  );

  const contentElement = !hasIssue ? (
    <NoIssueFound />
  ) : (
    <DumbListingContent>
      {issues.map(issue => {
        return (
          <Link key={issue.incident_id} to={issue.report_url} target="_blank">
            <ListingItem
              hasBottomBorder
              text={issue.comment ?? ''}
              leftIcon={
                <div className="text-darkGray2">
                  {issue.present ? <FaRegDotCircle /> : <FaRegCircle />}
                </div>
              }
            />
          </Link>
        );
      })}
    </DumbListingContent>
  );

  return <BaseCard title={titleElement} content={contentElement} />;
};

export const MemoizedIssuesList = memo(IssuesList);
