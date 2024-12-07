import { MdFolderOpen } from 'react-icons/md';

import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type {
  AccordionItemBuilds,
  BuildCountsResponse,
} from '@/types/tree/TreeDetails';

import { useBuildStatusCount } from '@/api/treeDetails';

import type { IStatusChart } from '@/components/StatusChart/StatusCharts';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';

import type { ILinkGroup } from '@/components/LinkGroup/LinkGroup';
import LinksGroup from '@/components/LinkGroup/LinkGroup';

import { Button } from '@/components/ui/button';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

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
  accordionData: AccordionItemBuilds;
  onClickShowBuild: (buildId: AccordionItemBuilds['id']) => void;
  openLogSheet?: () => void;
}

const AccordionBuildContent = ({
  accordionData,
  onClickShowBuild,
  openLogSheet,
}: IAccordionItems): JSX.Element => {
  const { data, status } = useBuildStatusCount(
    { buildId: accordionData.id ?? '' },
    { enabled: !!accordionData.id },
  );

  const onClickShowBuildHandler = useCallback(
    () => onClickShowBuild(accordionData.id),
    [accordionData.id, onClickShowBuild],
  );

  const links: ILinkGroup['links'] = useMemo(
    () => [
      accordionData.kernelImage
        ? {
            title: 'buildAccordion.kernelImage',
            icon: <MdFolderOpen className={blueText} />,
            linkText: <span>{`kernel/${accordionData.kernelImage}`}</span>,
          }
        : undefined,
      accordionData.kernelConfig
        ? {
            title: 'buildAccordion.kernelConfig',
            icon: <MdFolderOpen className={blueText} />,
            link: accordionData.kernelConfig,
            linkText: <FormattedMessage id="buildAccordion.kernelConfigPath" />,
          }
        : undefined,
      accordionData.dtb
        ? {
            title: 'buildAccordion.dtb',
            icon: <MdFolderOpen className={blueText} />,
            link: accordionData.dtb,
            linkText: <FormattedMessage id="buildAccordion.dtbs" />,
          }
        : undefined,
      accordionData.buildLogs
        ? {
            title: 'buildAccordion.buildLogs',
            icon: <MdFolderOpen className={blueText} />,
            linkText: <FormattedMessage id="buildAccordion.logs" />,
            onClick: openLogSheet,
          }
        : undefined,
      accordionData.systemMap
        ? {
            title: 'buildAccordion.systemMap',
            icon: <MdFolderOpen className={blueText} />,
            link: accordionData.systemMap,
            linkText: <FormattedMessage id="buildAccordion.systemMapPath" />,
          }
        : undefined,
      accordionData.modules
        ? {
            title: 'buildAccordion.modules',
            icon: <MdFolderOpen className={blueText} />,
            link: accordionData.modules,
            linkText: <FormattedMessage id="buildAccordion.modulesZip" />,
          }
        : undefined,
    ],
    [
      accordionData.buildLogs,
      accordionData.dtb,
      accordionData.kernelConfig,
      accordionData.kernelImage,
      accordionData.modules,
      accordionData.systemMap,
      openLogSheet,
    ],
  );

  return (
    <div className="flex flex-row justify-between">
      <QuerySwitcher data={data} status={status} skeletonClassname="h-[60px]">
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
  );
};

export default AccordionBuildContent;
