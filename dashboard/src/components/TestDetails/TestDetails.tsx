import { FormattedMessage, useIntl } from 'react-intl';

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

import { EMPTY_VALUE, truncateBigText, valueOrEmpty } from '@/lib/string';
import type { TTestDetails, TestStatusHistory } from '@/types/tree/TestDetails';
import { Sheet } from '@/components/Sheet';
import {
  useTestDetails,
  useTestIssues,
  useTestStatusHistory,
} from '@/api/testDetails';

import { RedirectFrom } from '@/types/general';

import type { SheetType } from '@/components/Sheet/LogOrJsonSheetContent';
import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import Section, { type ISection } from '@/components/Section/Section';
import IssueSection from '@/components/Issue/IssueSection';
import SectionGroup from '@/components/Section/SectionGroup';
import { getMiscSection } from '@/components/Section/MiscSection';
import { getFilesSection } from '@/components/Section/FilesSection';

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

import { isBadRequestError } from '@/utils/query';

import { MemoizedKcidevCommandButton } from '@/components/Footer/KcidevCommandButton';
import { createResultDetailsCommand } from '@/components/Footer/kcidevCommand';

import { isBoot } from '@/utils/test';

import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';

import { DetailsInfoCard } from '@/components/Cards/DetailsInfoCard';

import CopyButton from '@/components/Button/CopyButton';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';

import { HardwareRegistryCard } from '@/components/HardwareRegistry/HardwareRegistry';

import { StatusHistoryItem } from './StatusHistoryItem';

const TestDetailsSections = ({
  test,
  statusHistory,
  statusHistoryStatus,
  statusHistoryError,
  setSheetType,
  actions,
}: {
  test: TTestDetails;
  statusHistory?: TestStatusHistory;
  statusHistoryStatus: UseQueryResult['status'];
  statusHistoryError: UseQueryResult['error'];
  setSheetType: Dispatch<SetStateAction<SheetType>>;
  actions?: JSX.Element;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const historyState = useRouterState({ select: s => s.location.state });
  const searchParams = useSearch({ from: '/_main/test/$testId' });
  const hardwareId = getTestHardware({
    misc: test.environment_misc,
    compatibles: test.environment_compatible,
  });
  const hardware = hardwareId ?? formatMessage({ id: 'global.unknown' });

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

  const hardwareDetailsLink = useMemo(() => {
    if (!hardwareId) {
      return <span>{hardware}</span>;
    }

    return (
      <MemoizedLinkItem
        to="/hardware/$hardwareId"
        params={{ hardwareId }}
        search={{ diffFilter: { testOrigin: { [test.test_origin]: true } } }}
        state={s => s}
      >
        {hardware}
        <LinkIcon className="text-blue text-xl" />
      </MemoizedLinkItem>
    );
  }, [hardware, hardwareId, test.test_origin]);

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
              search={{
                diffFilter: { testOrigin: { [test.test_origin]: true } },
              }}
              state={s => s}
            >
              {compatible}
              <LinkIcon className="text-blue text-xl" />
            </MemoizedLinkItem>
          ),
        )}
      </div>
    );
  }, [test.environment_compatible, test.test_origin]);

  const registryInfo = test.registry;

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

  const hasRequiredTrackingFields = Boolean(
    test.path &&
      test.origin &&
      test.git_repository_url &&
      test.git_repository_branch &&
      test.config_name,
  );

  const regressionSection: ISection | undefined = useMemo(() => {
    const cannotFetchHistory =
      !hasRequiredTrackingFields ||
      (statusHistoryStatus === 'error' &&
        isBadRequestError(statusHistoryError));

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
                  status={
                    hasRequiredTrackingFields ? statusHistoryStatus : 'error'
                  }
                  data={statusHistory}
                  customError={
                    cannotFetchHistory ? (
                      <div className="text-weak-gray flex flex-col items-center py-6 text-2xl font-semibold">
                        <FormattedMessage id="testDetails.cannotFetchHistory" />
                      </div>
                    ) : (
                      <MemoizedSectionError
                        isLoading={statusHistoryStatus === 'pending'}
                        errorMessage={statusHistoryError?.message}
                        emptyLabel="global.error"
                        variant="warning"
                      />
                    )
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
    hasRequiredTrackingFields,
    regressionData,
    statusHistory,
    statusHistoryError,
    statusHistoryStatus,
  ]);

  const generalSection: ISection = useMemo(() => {
    const logUrl = valueOrEmpty(test.log_url);
    const gitUrl = valueOrEmpty(test.git_repository_url);

    return {
      title: test.path ?? test.id,
      subtitle: <ButtonOpenLogSheet setSheetToLog={setSheetToLog} />,
      actions,
      leftIcon: <StatusIcon status={test.status} showTooltip />,
      rightIcon: (
        <span className="text-dark-gray2 text-sm font-normal">
          {formatDate(valueOrEmpty(test.start_time), false, true)}
        </span>
      ),
      subsections: [
        {
          infos: [
            {
              children: (
                <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                  <DetailsInfoCard
                    cardTitle="testDetails.testInfo"
                    data={[
                      {
                        title: 'global.status',
                        linkText: test.status,
                        icon: <StatusIcon status={test.status} />,
                      },
                      {
                        title: 'testDetails.testOrigin',
                        linkText: valueOrEmpty(test.test_origin),
                      },
                      {
                        title: 'testDetails.testId',
                        linkText: test.id,
                        span: 2,
                      },
                      {
                        title: 'testDetails.buildInfo',
                        linkText: truncateBigText(test.build_id),
                        linkComponent: buildDetailsLink,
                        span: 2,
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
                        span: 2,
                      },
                      {
                        title: 'global.compatibles',
                        linkText: valueOrEmpty(
                          test.environment_compatible?.join(' | '),
                        ),
                        linkComponent: compatiblesLink,
                        span: 4,
                      },
                      {
                        title: 'global.logs',
                        linkText: logUrl,
                        link: test.log_url,
                        span: 4,
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
                        span: 2,
                        linkComponent: (
                          <span className="flex w-full min-w-0 items-center">
                            <TreeDetailsLink
                              className="min-w-0 flex-1"
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
                        title: 'global.commitTags',
                        linkText: valueOrEmpty(test.git_commit_tags?.[0]),
                        span: 2,
                      },
                      {
                        title: 'global.repository',
                        linkText: gitUrl,
                        link: test.git_repository_url,
                        span: 4,
                      },
                    ]}
                  />
                  <HardwareRegistryCard info={registryInfo} />
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
    actions,
    compatiblesLink,
    registryInfo,
  ]);

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: test.misc,
      title: formatMessage({ id: 'commonDetails.miscData' }),
    });
  }, [formatMessage, test.misc]);

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
    return [generalSection, regressionSection].filter(
      section => section !== undefined,
    );
  }, [generalSection, regressionSection]);

  const miscCards = [miscSection, environmentMiscSection].filter(
    section => section !== undefined,
  );
  const paired = miscCards.length > 0 && filesSection !== undefined;

  return (
    <>
      <SectionGroup sections={sectionsData} />
      {(miscCards.length > 0 || filesSection) && (
        <div
          className={
            paired
              ? 'grid grid-cols-1 items-start gap-4 lg:grid-cols-2'
              : 'flex flex-col gap-4'
          }
        >
          {miscCards.length > 0 && (
            <div className="flex flex-col gap-4">
              {miscCards.map(section => (
                <Section key={section.title} {...section} card />
              ))}
            </div>
          )}
          {filesSection && <Section {...filesSection} card />}
        </div>
      )}
    </>
  );
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
  const statusHistoryParams = useMemo(() => {
    if (
      !data?.path ||
      !data.origin ||
      !data.git_repository_url ||
      !data.git_repository_branch ||
      !data.config_name
    ) {
      return undefined;
    }

    return {
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
    };
  }, [data]);

  const {
    data: statusHistoryData,
    status: statusHistoryStatus,
    error: statusHistoryError,
  } = useTestStatusHistory(statusHistoryParams);

  const logData = useMemo(() => {
    if (!data) {
      return undefined;
    }
    return processLogData(testId, { type: 'test', ...data });
  }, [testId, data]);

  const [sheetType, setSheetType] = useState<SheetType>('log');
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
      <MemoizedKcidevCommandButton
        command={createResultDetailsCommand(command, testId)}
      />
    );
  }, [data?.path, testId]);

  const fallbackBreadcrumb = useMemo(
    () =>
      data && (
        <MemoizedTreeBreadcrumb
          locationMessage="test.details"
          tree={{
            treeName: data.tree_name,
            branch: data.git_repository_branch,
            id: data.git_commit_hash,
          }}
          searchParams={{
            origin: data.origin,
            treeInfo: {
              treeName: data.tree_name,
              gitBranch: data.git_repository_branch,
              gitUrl: data.git_repository_url,
              headCommitHash: data.git_commit_hash,
            },
          }}
        />
      ),
    [data],
  );

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
            {breadcrumb ?? fallbackBreadcrumb}
            {data && (
              <TestDetailsSections
                actions={kcidevComponent}
                test={data}
                statusHistory={statusHistoryData}
                statusHistoryStatus={statusHistoryStatus}
                statusHistoryError={statusHistoryError}
                setSheetType={setSheetType}
              />
            )}
            <IssueSection
              data={issueData}
              status={issueStatus}
              error={issueError?.message}
            />
          </div>
          <LogOrJsonSheetContent
            type={sheetType}
            logData={logData}
            hideIssueSection
          />
        </Sheet>
      </QuerySwitcher>
    </PageWithTitle>
  );
};

export default TestDetails;
