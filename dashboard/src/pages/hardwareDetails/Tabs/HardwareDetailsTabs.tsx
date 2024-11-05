import { useNavigate } from '@tanstack/react-router';

import type { ReactElement } from 'react';
import { useCallback, useMemo } from 'react';

import type { ITabItem } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import { zPossibleValidator } from '@/types/tree/TreeDetails';

import type { MessagesKey } from '@/locales/messages';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import BuildTab from './Build';

export type TreeDetailsTabRightElement = Record<
  Extract<
    MessagesKey,
    'treeDetails.builds' | 'treeDetails.boots' | 'treeDetails.tests'
  >,
  ReactElement
>;

export interface IHardwareDetailsTab {
  HardwareDetailsData: THardwareDetails;
}

const HardwareDetailsTabs = ({
  HardwareDetailsData,
}: IHardwareDetailsTab): JSX.Element => {
  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const onValueChange: (value: string) => void = useCallback(
    value => {
      const validatedValue = zPossibleValidator.parse(value);
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            currentTreeDetailsTab: validatedValue,
          };
        },
      });
    },
    [navigate],
  );
  // TODO: put i18n in global.
  const tabs: ITabItem[] = useMemo(
    () => [
      {
        name: 'treeDetails.builds',
        content: <BuildTab builds={HardwareDetailsData.builds} />,
        disabled: false,
      },
      {
        name: 'treeDetails.boots',
        content: <h1>Boots Tab</h1>,
        disabled: false,
      },
      {
        name: 'treeDetails.tests',
        content: <h1>Tests Tab</h1>,
        disabled: false,
      },
    ],
    [HardwareDetailsData],
  );

  return (
    <Tabs
      tabs={tabs}
      value="treeDetails.builds"
      onValueChange={onValueChange}
    />
  );
};

export default HardwareDetailsTabs;
