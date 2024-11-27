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
  HardwareDetailsData: THardwareDetails;
  hardwareId: string;
  filterListElement?: JSX.Element;
  countElements: TreeDetailsTabRightElement;
}

const HardwareDetailsTabs = ({
  HardwareDetailsData,
  hardwareId,
  filterListElement,
  countElements,
}: IHardwareDetailsTab): JSX.Element => {
  const { currentPageTab } = useSearch({
    from: '/hardware/$hardwareId/',
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
            builds={HardwareDetailsData.builds}
            hardwareId={hardwareId}
          />
        ),
        rightElement: countElements['global.builds'],
        disabled: false,
      },
      {
        name: 'global.boots',
        content: (
          <BootsTab boots={HardwareDetailsData.boots} hardwareId={hardwareId} />
        ),
        rightElement: countElements['global.boots'],
        disabled: false,
      },
      {
        name: 'global.tests',
        content: (
          <TestsTab tests={HardwareDetailsData.tests} hardwareId={hardwareId} />
        ),
        rightElement: countElements['global.tests'],
        disabled: false,
      },
    ],
    [
      HardwareDetailsData.boots,
      HardwareDetailsData.builds,
      HardwareDetailsData.tests,
      countElements,
      hardwareId,
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
