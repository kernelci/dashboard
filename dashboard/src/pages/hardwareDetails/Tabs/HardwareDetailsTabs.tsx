import { useNavigate, useSearch } from '@tanstack/react-router';

import type { ReactElement } from 'react';
import { useCallback, useMemo } from 'react';

import type { ITabItem } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export type TreeDetailsTabRightElement = Record<
  'global.builds' | 'global.boots' | 'global.tests',
  ReactElement
>;

export interface IHardwareDetailsTab {
  hardwareDetailsData: THardwareDetails;
  hardwareId: string;
  filterListElement?: JSX.Element;
  countElements: TreeDetailsTabRightElement;
}

const HardwareDetailsTabs = ({
  hardwareDetailsData,
  hardwareId,
  filterListElement,
  countElements,
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
            builds={hardwareDetailsData.builds}
            trees={hardwareDetailsData.trees}
            hardwareId={hardwareId}
          />
        ),
        rightElement: countElements['global.builds'],
        disabled: false,
      },
      {
        name: 'global.boots',
        content: (
          <BootsTab
            boots={hardwareDetailsData.boots}
            hardwareId={hardwareId}
            trees={hardwareDetailsData.trees}
          />
        ),
        rightElement: countElements['global.boots'],
        disabled: false,
      },
      {
        name: 'global.tests',
        content: (
          <TestsTab
            tests={hardwareDetailsData.tests}
            hardwareId={hardwareId}
            trees={hardwareDetailsData.trees}
          />
        ),
        rightElement: countElements['global.tests'],
        disabled: false,
      },
    ],
    [
      hardwareDetailsData.builds,
      hardwareDetailsData.trees,
      hardwareDetailsData.boots,
      hardwareDetailsData.tests,
      hardwareId,
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
