import { useCallback, useMemo, useState, type JSX } from 'react';

import { useNavigate } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import {
  treeDetailsFromMap,
  type TreeDetailsRouteFrom,
  type TreeDetailsSummary,
} from '@/types/tree/TreeDetails';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';

import {
  MemoizedCheckboxSection,
  MemoizedTimeRangeSection,
} from '@/components/Tabs/Filters';

import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import { getIssueFilterLabel } from '@/utils/utils';
import { UNCATEGORIZED_STRING } from '@/utils/constants/backend';

type PossibleTreeDetailsFilters = Pick<
  TFilter,
  | 'buildStatus'
  | 'bootStatus'
  | 'testStatus'
  | 'buildIssue'
  | 'bootIssue'
  | 'testIssue'
  | 'configs'
  | 'archs'
  | 'compilers'
  | 'hardware'
  | 'labs'
  | 'buildOrigin'
  | 'bootOrigin'
  | 'testOrigin'
>;

export const createFilter = (data: TreeDetailsSummary): TFilter => {
  const filters: PossibleTreeDetailsFilters = {};
  filters.buildStatus = {};
  filters.bootStatus = {};
  filters.testStatus = {};

  for (const s of testStatuses) {
    filters.buildStatus[s] = false;
    filters.bootStatus[s] = false;
    filters.testStatus[s] = false;
  }

  filters.buildIssue = {};
  filters.bootIssue = {};
  filters.testIssue = {};

  filters.configs = {};
  filters.archs = {};
  filters.compilers = {};

  filters.hardware = {};
  filters.labs = {};

  filters.buildOrigin = {};
  filters.bootOrigin = {};
  filters.testOrigin = {};

  // Filters affecting all tabs
  const allFilters = data.filters.all;
  for (const config of allFilters.configs) {
    filters.configs[config] = false;
  }
  for (const arch of allFilters.architectures) {
    filters.archs[arch] = false;
  }
  for (const compiler of allFilters.compilers) {
    filters.compilers[compiler] = false;
  }

  for (const h of data.common.hardware) {
    filters.hardware[h] = false;
  }

  // Build tab filters
  const buildFilters = data.filters.builds;
  for (const i of buildFilters.issues) {
    filters.buildIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] =
      false;
  }
  if (buildFilters.has_unknown_issue) {
    filters.buildIssue[UNCATEGORIZED_STRING] = false;
  }
  for (const o of buildFilters.origins) {
    filters.buildOrigin[o] = false;
  }

  // Boot tab filters
  const bootFilters = data.filters.boots;
  for (const i of bootFilters.issues) {
    filters.bootIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false;
  }
  if (bootFilters.has_unknown_issue) {
    filters.bootIssue[UNCATEGORIZED_STRING] = false;
  }
  for (const o of bootFilters.origins) {
    filters.bootOrigin[o] = false;
  }
  for (const l of bootFilters.labs) {
    filters.labs[l] = false;
  }

  // Test tab filters
  const testFilters = data.filters.tests;
  for (const i of testFilters.issues) {
    filters.testIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false;
  }
  if (testFilters.has_unknown_issue) {
    filters.testIssue[UNCATEGORIZED_STRING] = false;
  }
  for (const o of testFilters.origins) {
    filters.testOrigin[o] = false;
  }
  for (const l of testFilters.labs) {
    filters.labs[l] = false;
  }

  return filters;
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
  {
    title: 'filter.labs',
    subtitle: 'filter.labsSubtitle',
    sectionKey: 'labs',
    isGlobal: true,
  },
  {
    title: 'filter.buildOrigin',
    subtitle: 'filter.originsSubtitle',
    sectionKey: 'buildOrigin',
    isGlobal: false,
  },
  {
    title: 'filter.bootOrigin',
    subtitle: 'filter.originsSubtitle',
    sectionKey: 'bootOrigin',
    isGlobal: false,
  },
  {
    title: 'filter.testOrigin',
    subtitle: 'filter.originsSubtitle',
    sectionKey: 'testOrigin',
    isGlobal: false,
  },
];

interface ITreeDetailsFilter {
  paramFilter: TFilter;
  treeUrl: string;
  data: TreeDetailsSummary;
  urlFrom: TreeDetailsRouteFrom;
}

// TODO: some sections can be hidden if there is only 1 value for them (e.g., origins, labs)
const TreeDetailsFilter = ({
  paramFilter,
  treeUrl,
  data,
  urlFrom,
}: ITreeDetailsFilter): JSX.Element => {
  const navigate = useNavigate({
    from: treeDetailsFromMap[urlFrom],
  });

  const filter: TFilter = useMemo(() => {
    if (!data) {
      return {};
    }

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
      params: p => p,
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

  const drawerLink: IDrawerLink = useMemo(
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
