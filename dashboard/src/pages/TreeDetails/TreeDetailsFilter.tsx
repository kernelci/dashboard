import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate, useParams } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import type { TTreeTestsFullData } from '@/types/tree/TreeDetails';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';

import { Skeleton } from '@/components/Skeleton';

import {
  MemoizedCheckboxSection,
  MemoizedTimeRangeSection,
} from '@/components/Tabs/Filters';

import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';

import { useTreeDetails } from '@/api/treeDetails';

type TFilterValues = Record<string, boolean>;

interface ITreeDetailsFilter {
  paramFilter: TFilter;
  treeUrl: string;
}

export const createFilter = (data: TTreeTestsFullData | undefined): TFilter => {
  const buildStatus = { Success: false, Failed: false, Inconclusive: false };

  const bootStatus: TFilterValues = {};
  const testStatus: TFilterValues = {};
  testStatuses.forEach(s => {
    bootStatus[s] = false;
    testStatus[s] = false;
  });

  const buildIssue: TFilterValues = {};
  const bootIssue: TFilterValues = {};
  const testIssue: TFilterValues = {};

  const configs: TFilterValues = {};
  const archs: TFilterValues = {};
  const compilers: TFilterValues = {};

  const hardware: TFilterValues = {};

  if (data) {
    data.builds.forEach(b => {
      configs[b.config_name ?? 'Unknown'] = false;
      archs[b.architecture ?? 'Unknown'] = false;
      compilers[b.compiler ?? 'Unknown'] = false;
    });

    data.common.hardware.forEach(h => (hardware[h] = false));

    data.summary.builds.issues.forEach(i => (buildIssue[i.id] = false));
    data.summary.boots.issues.forEach(i => (bootIssue[i.id] = false));
    data.summary.tests.issues.forEach(i => (testIssue[i.id] = false));
  }

  return {
    buildStatus,
    configs,
    archs,
    compilers,
    bootStatus,
    testStatus,
    hardware,
    buildIssue,
    bootIssue,
    testIssue,
  };
};

const sectionTrees: ISectionItem[] = [
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
    title: 'filter.buildIssue',
    subtitle: 'filter.issueSubtitle',
    sectionKey: 'buildIssue',
  },
  {
    title: 'filter.bootIssue',
    subtitle: 'filter.issueSubtitle',
    sectionKey: 'bootIssue',
  },
  {
    title: 'filter.testIssue',
    subtitle: 'filter.issueSubtitle',
    sectionKey: 'testIssue',
  },
  {
    title: 'filter.hardware',
    subtitle: 'filter.hardwareSubtitle',
    sectionKey: 'hardware',
    isGlobal: true,
  },
  {
    title: 'global.configs',
    subtitle: 'filter.configsSubtitle',
    sectionKey: 'configs',
    isGlobal: true,
  },
  {
    title: 'global.architecture',
    subtitle: 'filter.architectureSubtitle',
    sectionKey: 'archs',
    isGlobal: true,
  },
  {
    title: 'global.compilers',
    subtitle: 'filter.compilersSubtitle',
    sectionKey: 'compilers',
    isGlobal: true,
  },
];
const TreeDetailsFilter = ({
  paramFilter,
  treeUrl,
}: ITreeDetailsFilter): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId' });

  const { data, isLoading } = useTreeDetails({
    treeId,
    // TODO : use  tree details summary
    variant: 'full',
  });

  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const filter: TFilter = useMemo(() => {
    return createFilter(data);
  }, [data]);

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
      title: 'filter.treeURL',
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
      {isLoading ? (
        <Skeleton>
          <FormattedMessage id="global.loading" />
        </Skeleton>
      ) : (
        <>
          <MemoizedCheckboxSection
            sections={sectionTrees}
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
            filter={filter}
            isTFilterObjectKeys={isTFilterObjectKeys}
          />
          <MemoizedTimeRangeSection
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
          />
        </>
      )}
    </FilterDrawer>
  );
};

export default TreeDetailsFilter;
