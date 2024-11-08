import { MdFolderOpen } from 'react-icons/md';

import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type {
  AccordionItemBuilds,
  BuildCountsResponse,
} from '@/types/tree/TreeDetails';

import { useBuildStatusCount } from '@/api/TreeDetails';

import { Sheet, SheetTrigger } from '@/components/Sheet';

import type { IStatusChart } from '@/components/StatusChart/StatusCharts';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';

import type { ILinkGroup } from '@/components/LinkGroup/LinkGroup';
import LinksGroup from '@/components/LinkGroup/LinkGroup';

import { Button } from '@/components/ui/button';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { LogSheet } from '@/pages/TreeDetails/Tabs/LogSheet';
import type { TPathTests } from '@/types/general';

export interface IBuildAccordionContent {
  testStatus: {
    failTests: number;
    errorTests: number;
    passTests: number;
    skipTests: number;
  };
  kernelImage?: string;
  buildLogs?: string;
  kernelConfig?: string;
  dtb?: string;
  systemMap?: string;
  modules?: string;
}

export interface ILinksGroup {
  kernelImage?: string;
  buildLogs?: string;
  kernelConfig?: string;
  dtb?: string;
  systemMap?: string;
  modules?: string;
}

const blueText = 'text-blue';

const AccordBuildStatusChart = ({
  buildCountsData,
}: {
  buildCountsData: BuildCountsResponse;
}): JSX.Element => {
  const { build_counts } = buildCountsData;

  const chartElements: IStatusChart['elements'] = useMemo(() => {
    return [
      {
        value: build_counts.pass_tests ?? 0,
        label: 'buildAccordion.testSuccess',
        color: Colors.Green,
      },
      {
        value: build_counts.error_tests ?? 0,
        label: 'buildAccordion.testError',
        color: Colors.Red,
      },
      {
        value: build_counts.skip_tests ?? 0,
        label: 'buildAccordion.testSkipped',
        color: Colors.DimGray,
      },
      {
        value: build_counts.miss_tests ?? 0,
        label: 'buildAccordion.testMiss',
        color: Colors.Gray,
      },
      {
        value: build_counts.fail_tests ?? 0,
        label: 'buildAccordion.testFail',
        color: Colors.Yellow,
      },
      {
        value: build_counts.done_tests ?? 0,
        label: 'buildAccordion.testDone',
        color: Colors.Blue,
      },
    ];
  }, [
    build_counts.done_tests,
    build_counts.error_tests,
    build_counts.fail_tests,
    build_counts.miss_tests,
    build_counts.pass_tests,
    build_counts.skip_tests,
  ]);

  return (
    <>
      {chartElements.some(slice => slice.value > 0) && (
        <div className="min-w-[400px]">
          <StatusChartMemoized
            type="chart"
            title={<FormattedMessage id="buildAccordion.testStatus" />}
            elements={chartElements}
          />
        </div>
      )}
    </>
  );
};

export interface IAccordionItems {
  accordionData: AccordionItemBuilds | TPathTests;
  onClickShowBuild: (buildId: AccordionItemBuilds['id']) => void;
}

const AccordionBuildContent = ({
  accordionData,
  onClickShowBuild,
}: IAccordionItems): JSX.Element => {
  //TODO: Fix the typing for not using as
  const contentData = accordionData as AccordionItemBuilds;

  const { data, status } = useBuildStatusCount(
    { buildId: contentData.id ?? '' },
    { enabled: !!contentData.id },
  );

  const onClickShowBuildHandler = useCallback(
    () => onClickShowBuild(contentData.id),
    [contentData.id, onClickShowBuild],
  );

  const links: ILinkGroup['links'] = useMemo(
    () => [
      contentData.kernelImage
        ? {
            title: 'buildAccordion.kernelImage',
            icon: <MdFolderOpen className={blueText} />,
            linkText: <span>{`kernel/${contentData.kernelImage}`}</span>,
          }
        : undefined,
      contentData.kernelConfig
        ? {
            title: 'buildAccordion.kernelConfig',
            icon: <MdFolderOpen className={blueText} />,
            link: contentData.kernelConfig,
            linkText: <FormattedMessage id="buildAccordion.kernelConfigPath" />,
          }
        : undefined,
      contentData.dtb
        ? {
            title: 'buildAccordion.dtb',
            icon: <MdFolderOpen className={blueText} />,
            link: contentData.dtb,
            linkText: <FormattedMessage id="buildAccordion.dtbs" />,
          }
        : undefined,
      contentData.buildLogs
        ? {
            title: 'buildAccordion.buildLogs',
            icon: <MdFolderOpen className={blueText} />,
            linkText: <FormattedMessage id="buildAccordion.logs" />,
            wrapperComponent: SheetTrigger,
          }
        : undefined,
      contentData.systemMap
        ? {
            title: 'buildAccordion.systemMap',
            icon: <MdFolderOpen className={blueText} />,
            link: contentData.systemMap,
            linkText: <FormattedMessage id="buildAccordion.systemMapPath" />,
          }
        : undefined,
      contentData.modules
        ? {
            title: 'buildAccordion.modules',
            icon: <MdFolderOpen className={blueText} />,
            link: contentData.modules,
            linkText: <FormattedMessage id="buildAccordion.modulesZip" />,
          }
        : undefined,
    ],
    [
      contentData.buildLogs,
      contentData.dtb,
      contentData.kernelConfig,
      contentData.kernelImage,
      contentData.modules,
      contentData.systemMap,
    ],
  );

  return (
    <>
      <Sheet>
        <div className="flex flex-row justify-between">
          <QuerySwitcher
            data={data}
            status={status}
            skeletonClassname="h-[60px]"
          >
            {data && <AccordBuildStatusChart buildCountsData={data} />}
          </QuerySwitcher>
          <div className="flex flex-col gap-8">
            <LinksGroup links={links} />
            <div className="flex flex-row gap-4">
              <Button
                variant="outline"
                className="w-min rounded-full border-2 border-black text-sm text-dimGray hover:bg-mediumGray"
                onClick={onClickShowBuildHandler}
              >
                <FormattedMessage id="buildAccordion.showMore" />
              </Button>
            </div>
          </div>
        </div>
        <LogSheet
          logExcerpt={data?.log_excerpt}
          logUrl={contentData.buildLogs}
        />
      </Sheet>
    </>
  );
};

export default AccordionBuildContent;
