import { useIntl } from 'react-intl';

import { GiFlatPlatform } from 'react-icons/gi';

import { useCallback, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';

import { PiComputerTowerThin } from 'react-icons/pi';
import { MdFolderOpen } from 'react-icons/md';

import { Link, useRouterState, useSearch } from '@tanstack/react-router';

import { FiLink } from 'react-icons/fi';

import { shouldTruncate, truncateBigText, valueOrEmpty } from '@/lib/string';
import type { TTestDetails } from '@/types/tree/TestDetails';
import { Sheet, SheetTrigger } from '@/components/Sheet';
import { useTestDetails, useTestIssues } from '@/api/testDetails';

import { RedirectFrom } from '@/types/general';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';
import { LogOrJsonSheetContent } from '@/components/Sheet/LogOrJsonSheetContent';
import type { ISection } from '@/components/Section/Section';
import { TooltipDateTime } from '@/components/TooltipDateTime';
import IssueSection from '@/components/Issue/IssueSection';
import SectionGroup from '@/components/Section/SectionGroup';
import { getMiscSection } from '@/components/Section/MiscSection';
import { getFilesSection } from '@/components/Section/FilesSection';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

const TestDetailsSections = ({
  test,
  setSheetType,
  setJsonContent,
}: {
  test: TTestDetails;
  setSheetType: Dispatch<SetStateAction<SheetType>>;
  setJsonContent: Dispatch<SetStateAction<IJsonContent | undefined>>;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const historyState = useRouterState({ select: s => s.location.state });
  const searchParams = useSearch({ from: '/test/$testId' });
  const hardware: string =
    test.environment_compatible?.join(' | ') ??
    formatMessage({ id: 'global.unknown' });

  const buildDetailsLink = useMemo(() => {
    let linkTo = '';
    let linkParams = {};
    if (historyState.from === RedirectFrom.Hardware && historyState.id) {
      linkTo = '/hardware/$hardwareId/build/$buildId';
      linkParams = { hardwareId: historyState.id, buildId: test.build_id };
    } else if (historyState.from === RedirectFrom.Tree && historyState.id) {
      linkTo = '/tree/$treeId/build/$buildId';
      linkParams = { treeId: historyState.id, buildId: test.build_id };
    } else {
      linkTo = '/build/$buildId';
      linkParams = { buildId: test.build_id };
    }

    return (
      <Link
        to={linkTo}
        params={linkParams}
        search={searchParams}
        className="flex flex-row items-center gap-1"
        target="_blank"
        rel="noreferrer"
      >
        {truncateBigText(test.build_id)}
        <FiLink className="text-blue" />
      </Link>
    );
  }, [historyState, test.build_id, searchParams]);

  const hasUsefulLogInfo = test.log_url || test.log_excerpt;

  const setSheetToLog = useCallback(
    (): void => setSheetType('log'),
    [setSheetType],
  );

  const generalSection: ISection = useMemo(() => {
    return {
      title: test.path,
      eyebrow: formatMessage({ id: 'test.details' }),
      subsections: [
        {
          infos: [
            {
              title: 'global.status',
              linkText: truncateBigText(test.status),
            },
            {
              title: 'global.path',
              linkText: valueOrEmpty(test.path),
            },
            {
              title: 'global.arch',
              linkText: valueOrEmpty(test.architecture),
              icon: test.architecture ? (
                <PiComputerTowerThin className="text-blue" />
              ) : undefined,
            },
            {
              title: 'global.compiler',
              linkText: valueOrEmpty(test.compiler),
            },
            {
              title: 'global.logs',
              icon: hasUsefulLogInfo ? (
                <MdFolderOpen className="text-blue" />
              ) : undefined,
              linkText: shouldTruncate(valueOrEmpty(test.log_url)) ? (
                <TruncatedValueTooltip value={test.log_url} isUrl={true} />
              ) : (
                valueOrEmpty(test.log_url)
              ),
              wrapperComponent: hasUsefulLogInfo ? SheetTrigger : undefined,
              onClick: hasUsefulLogInfo ? setSheetToLog : undefined,
            },
            {
              title: 'testDetails.gitCommitHash',
              linkText: valueOrEmpty(test.git_commit_hash),
              copyValue: valueOrEmpty(test.git_commit_hash),
            },
            {
              title: 'testDetails.gitRepositoryUrl',
              linkText: shouldTruncate(
                valueOrEmpty(test.git_repository_url),
              ) ? (
                <TruncatedValueTooltip
                  value={test.git_repository_url}
                  isUrl={true}
                />
              ) : (
                valueOrEmpty(test.git_repository_url)
              ),
              link: test.git_repository_url,
            },
            {
              title: 'testDetails.gitRepositoryBranch',
              linkText: valueOrEmpty(test.git_repository_branch),
            },
            {
              title: 'globalDetails.gitCommitTag',
              linkText: valueOrEmpty(test.git_commit_tags?.[0]),
            },
            {
              title: 'testDetails.buildInfo',
              linkText: truncateBigText(test.build_id),
              linkComponent: buildDetailsLink,
            },
            {
              title: 'global.hardware',
              linkText: hardware,
              icon: <GiFlatPlatform className="text-blue" />,
            },
            {
              title: 'global.startTime',
              linkText: (
                <TooltipDateTime
                  dateTime={test.start_time}
                  lineBreak={true}
                  showLabelTime={true}
                  showLabelTZ={true}
                />
              ),
            },
            {
              title: 'testDetails.jobId',
              linkText: test.id,
            },
          ],
        },
      ],
    };
  }, [
    test.path,
    test.status,
    test.architecture,
    test.compiler,
    test.log_url,
    test.git_commit_hash,
    test.git_repository_url,
    test.git_repository_branch,
    test.git_commit_tags,
    test.build_id,
    test.start_time,
    test.id,
    formatMessage,
    hasUsefulLogInfo,
    buildDetailsLink,
    hardware,
    setSheetToLog,
  ]);

  const miscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: test.misc,
      title: formatMessage({ id: 'globalDetails.miscData' }),
      setSheetType: setSheetType,
      setJsonContent: setJsonContent,
    });
  }, [formatMessage, test.misc, setSheetType, setJsonContent]);

  const environmentMiscSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getMiscSection({
      misc: test.environment_misc,
      title: formatMessage({ id: 'globalDetails.environmentMiscData' }),
    });
  }, [formatMessage, test.environment_misc]);

  const filesSection: ISection | undefined = useMemo(():
    | ISection
    | undefined => {
    return getFilesSection({
      outputFiles: test.output_files,
      title: formatMessage({ id: 'globalDetails.artifacts' }),
    });
  }, [formatMessage, test.output_files]);

  const sectionsData: ISection[] = useMemo(() => {
    return [
      generalSection,
      miscSection,
      environmentMiscSection,
      filesSection,
    ].filter(section => section !== undefined);
  }, [generalSection, miscSection, environmentMiscSection, filesSection]);

  return <SectionGroup sections={sectionsData} />;
};

interface TestsDetailsProps {
  breadcrumb?: JSX.Element;
  testId?: string;
}

const TestDetails = ({
  breadcrumb,
  testId,
}: TestsDetailsProps): JSX.Element => {
  const historyState = useRouterState({ select: s => s.location.state });
  const searchParams = useSearch({ from: '/test/$testId' });
  const { data, isLoading, status } = useTestDetails(testId ?? '');
  const { data: issueData, status: issueStatus } = useTestIssues(testId ?? '');

  const { formatMessage } = useIntl();

  const [sheetType, setSheetType] = useState<SheetType>('log');
  const [jsonContent, setJsonContent] = useState<IJsonContent>();

  return (
    <QuerySwitcher
      status={status}
      data={data}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={formatMessage({ id: 'testDetails.failedToFetch' })}
          emptyLabel={'global.error'}
        />
      }
    >
      <Sheet>
        <div className="w-100 px-5 pb-8">
          {breadcrumb}

          {data && (
            <TestDetailsSections
              test={data}
              setSheetType={setSheetType}
              setJsonContent={setJsonContent}
            />
          )}
          <IssueSection
            data={issueData}
            status={issueStatus}
            historyState={historyState}
            previousSearch={searchParams}
          />
        </div>
        <LogOrJsonSheetContent
          type={sheetType}
          jsonContent={jsonContent}
          logUrl={data?.log_url}
          logExcerpt={data?.log_excerpt}
        />
      </Sheet>
    </QuerySwitcher>
  );
};

export default TestDetails;
