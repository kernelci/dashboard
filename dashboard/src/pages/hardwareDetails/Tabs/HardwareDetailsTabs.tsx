import { useNavigate, useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import type { JSX, ReactElement } from 'react';
import { useCallback, useMemo } from 'react';

import type { UseQueryResult } from '@tanstack/react-query';

import type { ITabItem, TabRightElementRecord } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type {
  HardwareDetailsSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export interface IHardwareDetailsTab {
  hardwareId: string;
  filterListElement?: JSX.Element;
  countElements: TabRightElementRecord;
  fullDataResult?: UseQueryResult<THardwareDetails>;
  summaryData: HardwareDetailsSummary;
  hasSelectedTrees: boolean;
  headerExtra?: ReactElement;
}

const HardwareDetailsTabs = ({
  hardwareId,
  filterListElement,
  countElements,
  fullDataResult,
  summaryData,
  hasSelectedTrees,
  headerExtra,
}: IHardwareDetailsTab): JSX.Element => {
  const { currentPageTab } = useSearch({
    from: '/_main/hardware/$hardwareId',
  });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const onTabChange: (value: string) => void = useCallback(
    value => {
      const validatedValue = zPossibleTabValidator.parse(value);
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            currentPageTab: validatedValue,
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  const tabs: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        content: (
          <BuildTab
            hardwareId={hardwareId}
            trees={summaryData.common.trees}
            buildsSummary={summaryData.summary.builds}
            fullDataResult={fullDataResult}
          />
        ),
        rightElement: countElements['buildTab'],
        disabled: false,
      },
      {
        name: 'global.boots',
        content: (
          <BootsTab
            hardwareId={hardwareId}
            trees={summaryData.common.trees}
            bootsSummary={summaryData.summary.boots}
            fullDataResult={fullDataResult}
          />
        ),
        rightElement: countElements['bootTab'],
        disabled: false,
      },
      {
        name: 'global.tests',
        content: (
          <TestsTab
            hardwareId={hardwareId}
            trees={summaryData.common.trees}
            testsSummary={summaryData.summary.tests}
            fullDataResult={fullDataResult}
          />
        ),
        rightElement: countElements['testTab'],
        disabled: false,
      },
    ],
    [
      hardwareId,
      summaryData.common.trees,
      summaryData.summary.builds,
      summaryData.summary.boots,
      summaryData.summary.tests,
      fullDataResult,
      countElements,
    ],
  );

  if (!hasSelectedTrees) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <h3 className="text-lg font-medium">
            <FormattedMessage id="hardwareDetails.selectTreeTitle" />
          </h3>
          <p className="m-4 mx-auto max-w-lg">
            <FormattedMessage id="hardwareDetails.selectTreeMessage" />
          </p>
        </div>
      </div>
    );
  }

  return (
    <Tabs
      tabs={tabs}
      value={currentPageTab}
      onValueChange={onTabChange}
      filterListElement={filterListElement}
      headerExtra={headerExtra}
    />
  );
};

export default HardwareDetailsTabs;
