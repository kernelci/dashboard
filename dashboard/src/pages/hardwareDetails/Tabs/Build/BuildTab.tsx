import { FormattedMessage, useIntl } from 'react-intl';

import { memo, useMemo } from 'react';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';
import type {
  TFilterObjectsKeys,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';
import { sanitizeArchs, sanitizeBuilds, sanitizeConfigs } from '@/utils/utils';

import MemoizedIssuesList from '@/components/Cards/IssuesList';

import type { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';

import type { ISummaryItem, ISummaryTable } from '@/components/Summary/Summary';
import { DumbSummary } from '@/components/Summary/Summary';
import { BuildStatus, GroupedTestStatus } from '@/components/Status/Status';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';

import ListingItem from '@/components/ListingItem/ListingItem';

import { TableCell, TableCellWithLink, TableRow } from '@/components/ui/table';

import FilterLink from '../../HardwareDetailsFilterLink';

import { HardwareDetailsBuildsTable } from './HardwareDetailsBuildsTable';

interface TBuildTab {
  builds: THardwareDetails['builds'];
  hardwareId: string;
}

interface IErrorsSummaryBuild extends Pick<ISummaryTable, 'summaryBody'> {
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}

const StatusCard = ({
  buildsSummary,
  toggleFilterBySection,
}: {
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
  buildsSummary?: ITreeDetails['buildsSummary'];
}): JSX.Element => {
  const { formatMessage } = useIntl();
  if (!buildsSummary) return <></>;
  return (
    <BaseCard
      title={formatMessage({ id: 'buildTab.buildStatus' })}
      content={
        <StatusChartMemoized
          type="chart"
          pieCentralLabel={formatMessage({ id: 'global.executed' })}
          pieCentralDescription={
            <>
              {(buildsSummary.invalid ?? 0) +
                (buildsSummary.valid ?? 0) +
                (buildsSummary.null ?? 0)}
            </>
          }
          onLegendClick={(value: string) => {
            toggleFilterBySection(value, 'buildStatus');
          }}
          elements={[
            {
              value: buildsSummary.valid ?? 0,
              label: 'global.success',
              color: Colors.Green,
            },
            {
              value: buildsSummary.invalid ?? 0,
              label: 'global.failed',
              color: Colors.Red,
            },
            {
              value: buildsSummary.null ?? 0,
              label: 'global.inconclusive',
              color: Colors.Gray,
            },
          ]}
        />
      }
    />
  );
};

//TODO: put it in other file to be reused
export const MemoizedStatusCard = memo(StatusCard);

const SummaryItem = ({
  arch,
  compilers,
  onClickKey,
  leftIcon,
}: ISummaryItem): JSX.Element => {
  //const diffFilter = useDiffFilterParams(arch.text, 'archs');

  const compilersElement = useMemo(() => {
    return compilers?.map(compiler => (
      <FilterLink
        key={compiler}
        filterSection="compilers"
        filterValue={compiler}
      >
        {compiler}
      </FilterLink>
    ));
  }, [compilers]);

  return (
    <TableRow>
      <TableCellWithLink
        linkProps={{
          search: previousParams => previousParams,
        }}
      >
        <ListingItem
          onClick={onClickKey}
          warnings={arch.warnings}
          text={arch.text}
          leftIcon={leftIcon}
          success={arch.success}
          unknown={arch.unknown}
          errors={arch.errors}
        />
      </TableCellWithLink>
      <TableCell>
        <div className="flex flex-col gap-1">{compilersElement}</div>
      </TableCell>
    </TableRow>
  );
};

//TODO: put it in other file to be reused
export const MemoizedSummaryItem = memo(SummaryItem);

const ErrorsSummaryBuild = ({
  summaryBody,
  toggleFilterBySection,
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

//TODO: put it in other file to be reused
export const MemoizedErrorsSummaryBuild = memo(ErrorsSummaryBuild);

const ConfigsCard = ({
  configs,
}: {
  configs: ITreeDetails['configs'];
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}): JSX.Element => {
  const content = useMemo(() => {
    return (
      <DumbListingContent>
        {configs.map((item, i) => (
          <FilterLink key={i} filterSection="configs" filterValue={item.text}>
            <ListingItem
              text={item.text}
              leftIcon={
                <BuildStatus
                  valid={item.success}
                  invalid={item.errors}
                  unknown={item.unknown}
                />
              }
            />
          </FilterLink>
        ))}
      </DumbListingContent>
    );
  }, [configs]);

  return (
    <BaseCard
      title={<FormattedMessage id="global.configs" />}
      content={content}
    />
  );
};
//TODO: put it in other file to be reused
export const MemoizedConfigsCard = memo(ConfigsCard);

const BuildTab = ({ builds, hardwareId }: TBuildTab): JSX.Element => {
  /* const navigate = useNavigate({
    from: '/hardware/$hardwareId/',
  }); */

  //TODO: implement this function to filter details by data list

  const toggleFilterBySection = console.error;
  /* useCallback(
    (filterSectionKey: string, filterSection: TFilterObjectsKeys): void => {
      navigate({
        search: previousParams => {
          const { diffFilter: currentDiffFilter } = previousParams;
          const newFilter = structuredClone(currentDiffFilter);
          // This seems redundant but we do this to keep the pointer to newFilter[filterSection]
          newFilter[filterSection] = newFilter[filterSection] ?? {};
          const configs = newFilter[filterSection];
          if (configs[filterSectionKey]) {
            delete configs[filterSectionKey];
          } else {
            configs[filterSectionKey] = true;
          }

          return {
            ...previousParams,
            diffFilter: newFilter,
          };
        },
      });
    },
    [navigate],
  ); */

  const archSummary = useMemo(
    () => sanitizeArchs(builds.summary.architectures),
    [builds.summary.architectures],
  );

  const configsItems = useMemo(
    () => sanitizeConfigs(builds.summary.configs),
    [builds.summary.configs],
  );

  const buildItems = useMemo(
    () => sanitizeBuilds(builds.items),
    [builds.items],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            buildsSummary={builds.summary.builds}
          />
          <MemoizedErrorsSummaryBuild
            summaryBody={archSummary}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={builds.issues}
            failedWithUnknownIssues={builds.failedWithUnknownIssues}
          />
        </div>
        <MemoizedConfigsCard
          configs={configsItems}
          toggleFilterBySection={toggleFilterBySection}
        />
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          buildsSummary={builds.summary.builds}
        />
        <InnerMobileGrid>
          <MemoizedErrorsSummaryBuild
            summaryBody={archSummary}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedConfigsCard
            configs={configsItems}
            toggleFilterBySection={toggleFilterBySection}
          />
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={builds.issues}
          failedWithUnknownIssues={builds.failedWithUnknownIssues}
        />
      </MobileGrid>

      <div className="flex flex-col gap-4">
        <div className="text-lg">
          <FormattedMessage id="global.builds" />
        </div>
        <HardwareDetailsBuildsTable
          buildItems={buildItems}
          hardwareId={hardwareId}
        />
      </div>
    </div>
  );
};

export default BuildTab;
