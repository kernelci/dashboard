import type { Dispatch, SetStateAction } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate, useParams } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import type {
  TFilter,
  BuildsTab as TreeDetailsType,
  TTreeTestsFullData,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';
import { isTFilterObjectKeys } from '@/types/tree/TreeDetails';
import { useBuildsTab, useTestsTab } from '@/api/TreeDetails';
import { Skeleton } from '@/components/Skeleton';

import {
  MemoizedCheckboxSection,
  MemoizedTimeRangeSection,
} from '@/components/Tabs/Filters';

import type {
  RecordDiffBooleanType,
  RecordDiffNumberType,
} from '@/components/Tabs/tabsUtils';

import type { Section } from '@/components/Filter/CheckboxSection';

import { cleanFalseFilters } from './treeDetailsUtils';

type TFilterValues = Record<string, boolean>;

interface ITreeDetailsFilter {
  paramFilter: TFilter;
  treeUrl: string;
}

export const createFilter = (
  data: TreeDetailsType | undefined,
  testData: TTreeTestsFullData | undefined,
): TFilter => {
  const buildStatus = { Success: false, Failure: false };

  const bootStatus: TFilterValues = {};
  const testStatus: TFilterValues = {};
  testStatuses.forEach(s => {
    bootStatus[s] = false;
    testStatus[s] = false;
  });

  const configs: TFilterValues = {};
  const archs: TFilterValues = {};
  const compilers: TFilterValues = {};

  const hardware: TFilterValues = {};

  if (data)
    data.builds.forEach(b => {
      configs[b.config_name ?? 'Unknown'] = false;
      archs[b.architecture ?? 'Unknown'] = false;
      compilers[b.compiler ?? 'Unknown'] = false;
    });

  if (testData) testData.hardwareUsed.forEach(h => (hardware[h] = false));

  return {
    buildStatus,
    configs,
    archs,
    compilers,
    bootStatus,
    testStatus,
    hardware,
  };
};

const sectionTrees: Section[] = [
  {
    title: 'filter.buildStatus',
    subtitle: 'filter.statusSubtitle',
    sectionKey: 'buildStatus',
  },
  {
    title: 'filter.bootStatus',
    subtitle: 'filter.statusSubtitle',
    sectionKey: 'bootStatus',
  },
  {
    title: 'filter.testStatus',
    subtitle: 'filter.statusSubtitle',
    sectionKey: 'testStatus',
  },
  {
    title: 'filter.hardware',
    subtitle: 'filter.hardwareSubtitle',
    sectionKey: 'hardware',
  },
  {
    title: 'global.configs',
    subtitle: 'filter.configsSubtitle',
    sectionKey: 'configs',
  },
  {
    title: 'global.architecture',
    subtitle: 'filter.architectureSubtitle',
    sectionKey: 'archs',
  },
  {
    title: 'global.compilers',
    subtitle: 'filter.compilersSubtitle',
    sectionKey: 'compilers',
  },
];

const TreeDetailsFilter = ({
  paramFilter,
  treeUrl,
}: ITreeDetailsFilter): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });

  const { data, isLoading } = useBuildsTab({ treeId });

  const { data: testData, isLoading: testIsLoading } = useTestsTab({
    treeId,
    filter: {} as TTreeDetailsFilter,
  });

  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const filter: TFilter = useMemo(() => {
    return createFilter(data, testData);
  }, [data, testData]);

  const [diffFilter, setDiffFilter] = useState<TFilter>(paramFilter);

  const onClickFilterHandle = useCallback(() => {
    const cleanedFilter = cleanFalseFilters(diffFilter);
    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          diffFilter: cleanedFilter,
        };
      },
    });
  }, [diffFilter, navigate]);

  const onClickCancel = useCallback(() => {
    setDiffFilter(paramFilter);
  }, [paramFilter]);

  const handleOpenChange = useCallback(
    (_open: boolean) => {
      setDiffFilter(paramFilter);
    },
    [paramFilter],
  );

  const drawerLink: IDrawerLink['link'] = useMemo(
    () => ({
      title: 'filter.hardware',
      value: treeUrl,
      url: treeUrl,
    }),
    [treeUrl],
  );

  return (
    <FilterDrawer
      link={drawerLink}
      onFilter={onClickFilterHandle}
      onOpenChange={handleOpenChange}
      onCancel={onClickCancel}
    >
      {isLoading || testIsLoading ? (
        <Skeleton>
          <FormattedMessage id="global.loading" />
        </Skeleton>
      ) : (
        <>
          <MemoizedCheckboxSection
            sections={sectionTrees}
            setDiffFilter={
              setDiffFilter as Dispatch<SetStateAction<RecordDiffBooleanType>>
            }
            diffFilter={diffFilter as RecordDiffBooleanType}
            filter={filter as RecordDiffBooleanType}
            isTFilterObjectKeys={isTFilterObjectKeys}
          />
          <MemoizedTimeRangeSection
            setDiffFilter={
              setDiffFilter as Dispatch<SetStateAction<RecordDiffNumberType>>
            }
            diffFilter={diffFilter as RecordDiffNumberType}
          />
        </>
      )}
    </FilterDrawer>
  );
};

export default TreeDetailsFilter;
