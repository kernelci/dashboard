import { FormattedMessage, useIntl } from 'react-intl';

import { memo, useCallback, useMemo } from 'react';

import { useNavigate } from '@tanstack/react-router';

import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';

import type { TFilterObjectsKeys } from '@/types/tree/TreeDetails';
import type { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';
import { MemoizedErrorsSummaryBuild } from '@/pages/TreeDetails/Tabs/BuildCards';

import { BuildStatus } from '@/components/Status/Status';

import ListingItem from '@/components/ListingItem/ListingItem';

import { MemoizedIssuesList } from '@/pages/TreeDetails/Tabs/TestCards';

import FilterLink from '@/pages/TreeDetails/TreeDetailsFilterLink';

import { DesktopGrid, InnerMobileGrid, MobileGrid } from '../TabGrid';

import { TreeDetailsBuildsTable } from './TreeDetailsBuildsTable';

interface BuildTab {
  treeDetailsData: ITreeDetails;
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
      title={formatMessage({ id: 'treeDetails.buildStatus' })}
      content={
        <StatusChartMemoized
          type="chart"
          pieCentralLabel={formatMessage({ id: 'treeDetails.executed' })}
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
              label: 'treeDetails.success',
              color: Colors.Green,
            },
            {
              value: buildsSummary.invalid ?? 0,
              label: 'treeDetails.failed',
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
      title={<FormattedMessage id="treeDetails.configs" />}
      content={content}
    />
  );
};
//TODO: put it in other file to be reused
export const MemoizedConfigsCard = memo(ConfigsCard);

const BuildTab = ({ treeDetailsData }: BuildTab): JSX.Element => {
  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const toggleFilterBySection = useCallback(
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
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            buildsSummary={treeDetailsData.buildsSummary}
          />
          <MemoizedErrorsSummaryBuild
            summaryBody={treeDetailsData.architectures}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={treeDetailsData.issues || []}
          />
        </div>
        <div>
          <CommitNavigationGraph />
          <MemoizedConfigsCard
            configs={treeDetailsData.configs}
            toggleFilterBySection={toggleFilterBySection}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <CommitNavigationGraph />
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          buildsSummary={treeDetailsData.buildsSummary}
        />
        <InnerMobileGrid>
          <MemoizedErrorsSummaryBuild
            summaryBody={treeDetailsData.architectures}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedConfigsCard
            configs={treeDetailsData.configs}
            toggleFilterBySection={toggleFilterBySection}
          />
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={treeDetailsData.issues}
        />
      </MobileGrid>

      {treeDetailsData && (
        <div className="flex flex-col gap-4">
          <div className="text-lg">
            <FormattedMessage id="treeDetails.builds" />
          </div>

          <TreeDetailsBuildsTable buildItems={treeDetailsData.builds} />
        </div>
      )}
    </div>
  );
};

export default BuildTab;
