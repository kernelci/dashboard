import { useCallback, useMemo, useState } from 'react';

import { useNavigate } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import type { TreeDetailsSummary } from '@/types/tree/TreeDetails';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';

import {
  MemoizedCheckboxSection,
  MemoizedTimeRangeSection,
} from '@/components/Tabs/Filters';

import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import { getIssueFilterLabel } from '@/utils/utils';
import { UNCATEGORIZED_STRING } from '@/utils/constants/backend';

type TFilterValues = Record<string, boolean>;

interface ITreeDetailsFilter {
  paramFilter: TFilter;
  treeUrl: string;
  data: TreeDetailsSummary;
}

export const createFilter = (data: TreeDetailsSummary | undefined): TFilter => {
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
    data.filters.all.configs.forEach(config => (configs[config] = false));
    data.filters.all.architectures.forEach(arch => (archs[arch] = false));
    data.filters.all.compilers.forEach(
      compiler => (compilers[compiler] = false),
    );

    data.common.hardware.forEach(h => (hardware[h] = false));

    const buildFilters = data.filters.builds;
    buildFilters.issues.forEach(
      i =>
        (buildIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false),
    );
    if (buildFilters.has_unknown_issue) {
      buildIssue[UNCATEGORIZED_STRING] = false;
    }

    const bootFilters = data.filters.boots;
    bootFilters.issues.forEach(
      i =>
        (bootIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false),
    );
    if (bootFilters.has_unknown_issue) {
      bootIssue[UNCATEGORIZED_STRING] = false;
    }

    const testFilters = data.filters.tests;
    testFilters.issues.forEach(
      i =>
        (testIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false),
    );
    if (testFilters.has_unknown_issue) {
      testIssue[UNCATEGORIZED_STRING] = false;
    }
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
  data,
}: ITreeDetailsFilter): JSX.Element => {
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
      state: s => s,
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
    </FilterDrawer>
  );
};

export default TreeDetailsFilter;
