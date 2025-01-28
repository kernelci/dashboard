import { useNavigate, useSearch } from '@tanstack/react-router';

import type { ReactElement } from 'react';
import { useCallback, useMemo } from 'react';

import type { UseQueryResult } from '@tanstack/react-query';

import type { ITabItem } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type {
  HardwareSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export type TreeDetailsTabRightElement = Record<
  'global.builds' | 'global.boots' | 'global.tests',
  ReactElement
>;

export interface IHardwareDetailsTab {
  hardwareId: string;
  filterListElement?: JSX.Element;
  countElements: TreeDetailsTabRightElement;
  fullDataResult?: UseQueryResult<THardwareDetails>;
  summaryData: HardwareSummary;
}

const HardwareDetailsTabs = ({
  hardwareId,
  filterListElement,
  countElements,
  fullDataResult,
  summaryData,
}: IHardwareDetailsTab): JSX.Element => {
  const { currentPageTab } = useSearch({
    from: '/hardware/$hardwareId',
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
            trees={summaryData.trees}
            buildsSummary={summaryData.builds}
            fullDataResult={fullDataResult}
          />
        ),
        rightElement: countElements['global.builds'],
        disabled: false,
      },
      {
        name: 'global.boots',
        content: (
          <BootsTab
            hardwareId={hardwareId}
            trees={summaryData.trees}
            bootsSummary={summaryData.boots}
            fullDataResult={fullDataResult}
          />
        ),
        rightElement: countElements['global.boots'],
        disabled: false,
      },
      {
        name: 'global.tests',
        content: (
          <TestsTab
            hardwareId={hardwareId}
            trees={summaryData.trees}
            testsSummary={summaryData.tests}
            fullDataResult={fullDataResult}
          />
        ),
        rightElement: countElements['global.tests'],
        disabled: false,
      },
    ],
    [
      hardwareId,
      summaryData.trees,
      summaryData.builds,
      summaryData.boots,
      summaryData.tests,
      fullDataResult,
      countElements,
    ],
  );

  return (
    <Tabs
      tabs={tabs}
      value={currentPageTab}
      onValueChange={onTabChange}
      filterListElement={filterListElement}
    />
  );
};

export default HardwareDetailsTabs;
