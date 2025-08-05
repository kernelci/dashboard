import { FormattedMessage, useIntl } from 'react-intl';
import { roundToNearestMinutes } from 'date-fns';

import { Fragment, useCallback, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction, JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import {
  useParams,
  useNavigate,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { MdChevronRight } from 'react-icons/md';

import type { UseQueryResult } from '@tanstack/react-query';

import {
  EMPTY_VALUE,
  shouldTruncate,
  truncateBigText,
  valueOrEmpty,
} from '@/lib/string';
import type { TTestDetails, TestStatusHistory } from '@/types/tree/TestDetails';
import { Sheet } from '@/components/Sheet';
import {
  useTestDetails,
  useTestIssues,
  useTestStatusHistory,
} from '@/api/testDetails';

import { RedirectFrom } from '@/types/general';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';
import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import type { ISection } from '@/components/Section/Section';
import IssueSection from '@/components/Issue/IssueSection';
import SectionGroup from '@/components/Section/SectionGroup';
import { getMiscSection } from '@/components/Section/MiscSection';
import { getFilesSection } from '@/components/Section/FilesSection';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { LinkIcon } from '@/components/Icons/Link';
import { StatusIcon } from '@/components/Icons/StatusIcons';

import PageWithTitle from '@/components/PageWithTitle';
import { formatDate, getTitle } from '@/utils/utils';
import { getTestHardware } from '@/lib/test';

import { MemoizedTestDetailsOGTags } from '@/components/OpenGraphTags/TestDetailsOGTags';
import ButtonOpenLogSheet from '@/components/Button/ButtonOpenLogSheet';

import { TooltipIcon } from '@/components/Icons/TooltipIcon';

import { Badge } from '@/components/ui/badge';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import MemoizedLinkItem from '@/components/DetailsLink';
import { processLogData } from '@/hooks/useLogData';

import { dateObjectToTimestampInSeconds, daysToSeconds } from '@/utils/date';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import { isBoot } from '@/utils/test';

import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import { DetailsInfoCard } from '@/components/Cards/DetailsInfoCard';

import CopyButton from '@/components/Button/CopyButton';

import { StatusHistoryItem } from './StatusHistoryItem';

const TestDetailsSections = ({
  test,
  statusHistory,
  statusHistoryStatus,
  statusHistoryError,
  setSheetType,
  setJsonContent,
}: {
  test: TTestDetails;
  statusHistory?: TestStatusHistory;
  statusHistoryStatus: UseQueryResult['status'];
  statusHistoryError: UseQueryResult['error'];
  setSheetType: Dispatch<SetStateAction<SheetType>>;
  setJsonContent: Dispatch<SetStateAction<IJsonContent | undefined>>;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const historyState = useRouterState({ select: s => s.location.state });
  const searchParams = useSearch({ from: '/_main/test/$testId' });
  const hardware: string = useMemo(() => {
    return getTestHardware({
      misc: test.environment_misc,
      compatibles: test.environment_compatible,
      defaultValue: formatMessage({ id: 'global.unknown' }),
    });
  }, [formatMessage, test.environment_compatible, test.environment_misc]);

  const buildDetailsLink = useMemo(() => {
    let linkTo: LinkProps['to'] = '/build/$buildId';
    let linkParams = {};

    if (historyState.from === RedirectFrom.Hardware && historyState.id) {
      linkTo = '/hardware/$hardwareId/build/$buildId';
      linkParams = { hardwareId: historyState.id, buildId: test.build_id };
    } else if (historyState.from === RedirectFrom.Tree && historyState.id) {
      linkTo = '/build/$buildId';
      linkParams = { buildId: test.build_id };
    } else {
      linkParams = { buildId: test.build_id };
    }

    return (
      <MemoizedLinkItem to={linkTo} params={linkParams} search={searchParams}>
        {truncateBigText(test.build_id)}
        <LinkIcon className="text-blue text-xl" />
      </MemoizedLinkItem>
    );
  }, [historyState, test.build_id, searchParams]);

  const endTimestampInSeconds = dateObjectToTimestampInSeconds(
    roundToNearestMinutes(new Date(), {
      nearestTo: 30,
    }),
  );
  const startTimestampInSeconds =
    endTimestampInSeconds - daysToSeconds(REDUCED_TIME_SEARCH);

  const hardwareDetailsLink = useMemo(() => {
    if (hardware === formatMessage({ id: 'global.unknown' })) {
      return <span>{hardware}</span>;
    }

    return (
      <MemoizedLinkItem
        to="/hardware/$hardwareId"
        params={{ hardwareId: hardware }}
        state={s => s}
        search={{
          origin: searchParams.origin,
          startTimestampInSeconds: startTimestampInSeconds,
          endTimestampInSeconds: endTimestampInSeconds,
        }}
      >
        {hardware}
        <LinkIcon className="text-blue text-xl" />
      </MemoizedLinkItem>
    );
  }, [
    searchParams,
    hardware,
    formatMessage,
    startTimestampInSeconds,
    endTimestampInSeconds,
  ]);

  const compatiblesLink = useMemo(() => {
    if (!test.environment_compatible) {
      return <span>{EMPTY_VALUE}</span>;
    }

    return (
      <div className="flex flex-wrap gap-2">
        {test.environment_compatible.map(
          (compatible: string): JSX.Element => (
            <MemoizedLinkItem
              key={compatible}
              to="/hardware/$hardwareId"
              params={{ hardwareId: compatible }}
              state={s => s}
              search={{
                origin: searchParams.origin,
                startTimestampInSeconds: startTimestampInSeconds,
                endTimestampInSeconds: endTimestampInSeconds,
              }}
            >
              {compatible}
              <LinkIcon className="text-blue text-xl" />
            </MemoizedLinkItem>
          ),
        )}
      </div>
    );
  }, [
    searchParams,
    test.environment_compatible,
    startTimestampInSeconds,
    endTimestampInSeconds,
  ]);

  const setSheetToLog = useCallback(
    (): void => setSheetType('log'),
    [setSheetType],
  );

  const regressionData: JSX.Element[] | undefined = useMemo(() => {
    return statusHistory?.status_history
      .slice()
      .reverse()
      .map((historyItem, index) => {
        return (
          <Fragment key={historyItem.id}>
            <StatusHistoryItem
              historyItem={historyItem}
              isCurrentTest={historyItem.id === test.id}
            />
            {index !== statusHistory.status_history.length - 1 && (
              <MdChevronRight className="mt-6 size-6" />
            )}
          </Fragment>
        );
      });
  }, [statusHistory?.status_history, test.id]);

  const regressionSection: ISection | undefined = useMemo(() => {
    if (statusHistoryStatus === 'error') {
      return;
    }

    const regressionTypeTooltip: string | null = ((): string | null => {
      switch (statusHistory?.regression_type) {
        case 'fixed':
          return formatMessage({ id: 'testDetails.regressionTooltip.fixed' });
        case 'regression':
          return formatMessage({
            id: 'testDetails.regressionTooltip.regression',
          });
        case 'unstable':
          return formatMessage({
            id: 'testDetails.regressionTooltip.unstable',
          });
        default:
          return null;
      }
    })();

    const regressionSubtitle = (
      <div>
        <Tooltip>
          <TooltipTrigger>
            <Badge variant="blueTag">{statusHistory?.regression_type}</Badge>
          </TooltipTrigger>
          <TooltipContent className="whitespace-pre-line">
            <FormattedMessage
              id="testDetails.regressionTypeTooltip"
              values={{
                fixedTooltip: formatMessage({
                  id: 'testDetails.regressionTooltip.fixed',
                }),
                regressionTooltip: formatMessage({
                  id: 'testDetails.regressionTooltip.regression',
                }),
                unstableTooltip: formatMessage({
                  id: 'testDetails.regressionTooltip.unstable',
                }),
              }}
            />
          </TooltipContent>
        </Tooltip>
        {regressionTypeTooltip !== null && (
          <span> - {regressionTypeTooltip}</span>
        )}
      </div>
    );

    return {
      title: formatMessage({ id: 'testDetails.statusHistory' }),
      rightIcon: (
        <TooltipIcon
          tooltipId="testDetails.statusHistoryTooltip"
          tooltipValues={{ amount: statusHistory?.status_history.length }}
          iconClassName="size-5"
          contentClassName="whitespace-pre-line"
        />
      ),
      subtitle: statusHistory && regressionSubtitle,
      subsections: [
        {
          infos: [
            {
              children: (
                <QuerySwitcher
                  skeletonClassname="h-[100px]"
                  status={statusHistoryStatus}
                  data={statusHistory}
                  customError={
                    <MemoizedSectionError
                      isLoading={statusHistoryStatus === 'pending'}
                      errorMessage={statusHistoryError?.message}
                      emptyLabel="global.error"
                      variant="warning"
                    />
                  }
                >
                  <div className="flex items-center">{regressionData}</div>
                </QuerySwitcher>
              ),
            },
          ],
        },
      ],
    };
  }, [
    formatMessage,
    regressionData,
    statusHistory,
    statusHistoryError?.message,
    statusHistoryStatus,
  ]);

  const generalSection: ISection = useMemo(() => {
    const logUrl = valueOrEmpty(test.log_url);
    const gitUrl = valueOrEmpty(test.git_repository_url);

    return {
      title: test.path ?? test.id,
      subtitle: (
        <div>
          <span className="text-[18px]">
            {formatDate(valueOrEmpty(test.start_time), false, true)}
          </span>
          <ButtonOpenLogSheet setSheetToLog={setSheetToLog} />
        </div>
      ),
      leftIcon: <StatusIcon status={test.status} showTooltip />,
      subsections: [
        {
          infos: [
            {
              children: (
                <div className="grid grid-cols-2 gap-4">
                  <DetailsInfoCard
                    cardTitle="testDetails.testInfo"
                    data={[
                      {
                        title: 'global.status',
                        linkText: test.status,
                        icon: <StatusIcon status={test.status} />,
                      },
                      {
                        title: 'global.hardware',
                        linkText: hardware,
                        linkComponent: hardwareDetailsLink,
                      },
                      {
                        title: 'global.architecture',
                        linkText: valueOrEmpty(test.architecture),
                      },
                      {
                        title: 'global.compiler',
                        linkText: valueOrEmpty(test.compiler),
                      },
                      {
                        title: 'global.config',
                        linkText: valueOrEmpty(test.config_name),
                      },
                      {
                        title: 'testDetails.buildInfo',
                        linkText: truncateBigText(test.build_id),
                        linkComponent: buildDetailsLink,
                      },
                      {
                        title: 'global.compatibles',
                        linkText: valueOrEmpty(
                          test.environment_compatible?.join(' | '),
                        ),
                        linkComponent: compatiblesLink,
                      },
                      {
                        title: 'global.logs',
                        linkText: shouldTruncate(logUrl) ? (
                          <TruncatedValueTooltip value={logUrl} isUrl />
                        ) : (
                          logUrl
                        ),
                        link: test.log_url,
                        icon: test.log_url ? (
                          <LinkIcon className="text-blue text-xl" />
                        ) : undefined,
                      },
                      {
                        title: 'testDetails.testId',
                        linkText: test.id,
                      },
                    ]}
                  />
                  <DetailsInfoCard
                    cardTitle="commonDetails.gitInfo"
                    data={[
                      {
                        title: 'global.tree',
                        linkText: valueOrEmpty(test.tree_name),
                      },
                      {
                        title: 'globalTable.branch',
                        linkText: valueOrEmpty(test.git_repository_branch),
                      },
                      {
                        title: 'global.commitHash',
                        linkComponent: (
                          <span className="flex">
                            <TreeDetailsLink
                              treeName={test.tree_name}
                              gitBranch={test.git_repository_branch}
                              commitHash={test.git_commit_hash}
                              gitUrl={test.git_repository_url}
                            />
                            {test.git_commit_hash && (
                              <CopyButton value={test.git_commit_hash} />
                            )}
                          </span>
                        ),
                      },
                      {
                        title: 'global.repository',
                        linkText: shouldTruncate(gitUrl) ? (
                          <TruncatedValueTooltip value={gitUrl} isUrl />
                        ) : (
                          gitUrl
                        ),
                        link: test.git_repository_url,
                        icon: test.git_repository_url ? (
                          <LinkIcon className="text-blue text-xl" />
                        ) : undefined,
                      },
                      {
                        title: 'global.commitTags',
                        linkText: valueOrEmpty(test.git_commit_tags?.[0]),
                      },
                    ]}
                  />
                </div>
              ),
            },
          ],
        },
      ],
    };
  }, [
    test,
    setSheetToLog,
    hardware,
    hardwareDetailsLink,
    buildDetailsLink,
    compatiblesLink,
  ]);

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: test.misc,
      title: formatMessage({ id: 'commonDetails.miscData' }),
      setSheetType: setSheetType,
      setJsonContent: setJsonContent,
    });
  }, [formatMessage, test.misc, setSheetType, setJsonContent]);

  const environmentMiscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: test.environment_misc,
      title: formatMessage({ id: 'commonDetails.environmentMiscData' }),
    });
  }, [formatMessage, test.environment_misc]);

  const filesSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getFilesSection({
      inputFiles: test.input_files,
      outputFiles: test.output_files,
      title: formatMessage({ id: 'commonDetails.artifacts' }),
    });
  }, [formatMessage, test.input_files, test.output_files]);

  const sectionsData: ISection[] = useMemo(() => {
    return [
      generalSection,
      regressionSection,
      miscSection,
      environmentMiscSection,
      filesSection,
    ].filter(section => section !== undefined);
  }, [
    generalSection,
    regressionSection,
    miscSection,
    environmentMiscSection,
    filesSection,
  ]);

  return <SectionGroup sections={sectionsData} />;
};

interface TestsDetailsProps {
  breadcrumb?: JSX.Element;
}

const TestDetails = ({ breadcrumb }: TestsDetailsProps): JSX.Element => {
  const { testId } = useParams({ from: '/_main/test/$testId' });

  const { formatMessage } = useIntl();
  const { logOpen } = useSearch({ from: '/_main/test/$testId' });
  const navigate = useNavigate({ from: '/test/$testId' });

  const { data, isLoading, status, error } = useTestDetails(testId ?? '');
  const {
    data: issueData,
    status: issueStatus,
    error: issueError,
  } = useTestIssues(testId ?? '', data !== undefined);
  const {
    data: statusHistoryData,
    status: statusHistoryStatus,
    error: statusHistoryError,
  } = useTestStatusHistory(
    data !== undefined
      ? {
          path: data.path,
          origin: data.origin,
          git_repository_url: data.git_repository_url,
          git_repository_branch: data.git_repository_branch,
          platform:
            typeof data.environment_misc?.['platform'] === 'string'
              ? data.environment_misc['platform']
              : undefined,
          current_test_start_time: data.start_time,
          config_name: data.config_name,
          field_timestamp: data.field_timestamp,
        }
      : undefined,
  );

  const logData = useMemo(() => {
    if (!data) {
      return undefined;
    }
    return processLogData(testId, { type: 'test', ...data });
  }, [testId, data]);

  const [sheetType, setSheetType] = useState<SheetType>('log');
  const [jsonContent, setJsonContent] = useState<IJsonContent>();
  const logOpenChange = useCallback(
    (isOpen: boolean) =>
      navigate({ search: s => ({ ...s, logOpen: isOpen }), state: s => s }),
    [navigate],
  );

  const testDetailsTabTitle: string = useMemo(() => {
    return formatMessage(
      { id: 'title.testDetails' },
      { testName: getTitle(data?.path, isLoading) },
    );
  }, [data?.path, formatMessage, isLoading]);

  const kcidevComponent = useMemo(() => {
    const command = isBoot(data?.path) ? 'boot' : 'test';

    return (
      <MemoizedKcidevFooter
        commandGroup={'details'}
        args={{
          cmdName: command,
          id: testId,
          'download-logs': true,
          json: true,
        }}
      />
    );
  }, [data?.path, testId]);

  return (
    <PageWithTitle title={testDetailsTabTitle}>
      <MemoizedTestDetailsOGTags title={testDetailsTabTitle} data={data} />
      <QuerySwitcher
        status={status}
        data={data}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel="testDetails.notFound"
          />
        }
      >
        <Sheet open={logOpen} onOpenChange={logOpenChange}>
          <div className="flex flex-col gap-4 pb-10">
            {breadcrumb}

            {data && (
              <TestDetailsSections
                test={data}
                statusHistory={statusHistoryData}
                statusHistoryStatus={statusHistoryStatus}
                statusHistoryError={statusHistoryError}
                setSheetType={setSheetType}
                setJsonContent={setJsonContent}
              />
            )}
            <IssueSection
              data={issueData}
              status={issueStatus}
              error={issueError?.message}
            />
            {kcidevComponent}
          </div>
          <LogOrJsonSheetContent
            type={sheetType}
            jsonContent={jsonContent}
            logData={logData}
            hideIssueSection
          />
        </Sheet>
      </QuerySwitcher>
    </PageWithTitle>
  );
};

export default TestDetails;
