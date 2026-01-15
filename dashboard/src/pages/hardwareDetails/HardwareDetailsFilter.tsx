import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import { Skeleton } from '@/components/Skeleton';

import {
  MemoizedCheckboxSection,
  MemoizedTimeRangeSection,
  MemoizedTreeSelectSection,
  NO_VALID_INDEX,
} from '@/components/Tabs/Filters';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';
import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import type { HardwareDetailsSummary } from '@/types/hardware/hardwareDetails';
import { getIssueFilterLabel } from '@/utils/utils';
import { UNCATEGORIZED_STRING } from '@/utils/constants/backend';

type TFilterValues = Record<string, boolean>;

interface IHardwareDetailsFilter {
  paramFilter: TFilter;
  hardwareName: string;
  data: HardwareDetailsSummary | undefined;
  selectedTrees: number[] | null;
}

type TFilterCreate = TFilter & {
  treeIndexes: number[];
};

export const createFilter = (
  data: HardwareDetailsSummary | undefined,
): TFilterCreate => {
  const buildStatus: TFilterValues = {};
  const bootStatus: TFilterValues = {};
  const testStatus: TFilterValues = {};
  testStatuses.forEach(s => {
    buildStatus[s] = false;
    bootStatus[s] = false;
    testStatus[s] = false;
  });

  const buildIssue: TFilterValues = {};
  const bootIssue: TFilterValues = {};
  const testIssue: TFilterValues = {};

  const configs: TFilterValues = {};
  const archs: TFilterValues = {};
  const compilers: TFilterValues = {};
  const trees: TFilterValues = {};
  const compatibles: TFilterValues = {};
  const treeIndexes: number[] = [];

  const labs: TFilterValues = {};

  if (data) {
    // Global filters
    data.common.trees.forEach(tree => {
      const treeIdx = Number(tree.index);
      const treeName = tree.tree_name ?? 'Unknown';
      const treeBranch = tree.git_repository_branch ?? 'Unknown';

      let treeNameBranch = `${treeName}/${treeBranch}`;

      if (treeName === 'Unknown' && treeBranch === 'Unknown') {
        treeNameBranch = 'Unknown';
      }

      trees[`${treeNameBranch}__${treeIdx}`] = true;
      treeIndexes.push(treeIdx);
    });

    data.common.compatibles.forEach(c => (compatibles[c] = false));

    data.filters.all.architectures.forEach(arch => {
      archs[arch ?? 'Unknown'] = false;
    });
    data.filters.all.compilers.forEach(compiler => {
      compilers[compiler ?? 'Unknown'] = false;
    });
    data.filters.all.configs.forEach(config => {
      configs[config ?? 'Unknown'] = false;
    });

    // Build filters
    const buildFilters = data.filters.builds;
    buildFilters.issues.forEach(
      i =>
        (buildIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false),
    );
    if (buildFilters.has_unknown_issue) {
      buildIssue[UNCATEGORIZED_STRING] = false;
    }

    // Boot filters
    const bootFilters = data.filters.boots;
    bootFilters.issues.forEach(
      i =>
        (bootIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false),
    );
    if (bootFilters.has_unknown_issue) {
      bootIssue[UNCATEGORIZED_STRING] = false;
    }
    bootFilters.labs.forEach(lab => {
      labs[lab] = false;
    });

    // Test filters
    const testFilters = data.filters.tests;
    testFilters.issues.forEach(
      i =>
        (testIssue[getIssueFilterLabel({ id: i[0], version: i[1] })] = false),
    );
    if (testFilters.has_unknown_issue) {
      testIssue[UNCATEGORIZED_STRING] = false;
    }
    testFilters.labs.forEach(lab => {
      labs[lab] = false;
    });
  }

  return {
    buildStatus,
    configs,
    archs,
    compilers,
    bootStatus,
    testStatus,
    trees,
    treeIndexes,
    buildIssue,
    bootIssue,
    testIssue,
    hardware: compatibles,
    labs,
  };
};

const sectionHardware: ISectionItem[] = [
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
    title: 'global.compatibles',
    subtitle: 'filter.compatiblesSubtitle',
    sectionKey: 'hardware',
    isGlobal: true,
  },
  {
    title: 'filter.labs',
    subtitle: 'filter.labsSubtitle',
    sectionKey: 'labs',
    isGlobal: true,
  },
];

const HardwareDetailsFilter = ({
  paramFilter,
  hardwareName,
  data,
  selectedTrees,
}: IHardwareDetailsFilter): JSX.Element => {
  const isLoading = false;

  const navigate = useNavigate({
    from: '/hardware/$hardwareId',
  });

  const filter: TFilterCreate = useMemo(() => {
    return createFilter(data);
  }, [data]);

  const [diffFilter, setDiffFilter] = useState<TFilter>(paramFilter);
  const [treeIndexes, setTreeIndexes] = useState<number[]>([]);

  useEffect(() => {
    const initialTrees =
      selectedTrees && selectedTrees.length > 0
        ? selectedTrees
        : filter.treeIndexes;

    setTreeIndexes(initialTrees || []);
  }, [selectedTrees, filter]);

  const onClickFilterHandle = useCallback(() => {
    const cleanedFilter = cleanFalseFilters(diffFilter);
    navigate({
      search: previousSearch => {
        return {
          ...previousSearch,
          treeIndexes,
          diffFilter: cleanedFilter,
        };
      },
      state: s => s,
    });
  }, [diffFilter, navigate, treeIndexes]);

  const onClickCancel = useCallback(() => {
    setDiffFilter(paramFilter);
  }, [paramFilter]);

  const handleOpenChange = useCallback(
    (_open: boolean) => {
      setDiffFilter(paramFilter);
    },
    [paramFilter],
  );

  const handleSelectTree = useCallback(
    (value: string) => {
      const idx = Number(value.split('__')[1] ?? NO_VALID_INDEX);

      if (treeIndexes.includes(idx)) {
        setTreeIndexes(treeIndexes.filter(i => i !== idx));
      } else {
        setTreeIndexes([...treeIndexes, idx]);
      }
    },
    [treeIndexes],
  );

  const drawerLink: IDrawerLink = useMemo(
    () => ({
      title: 'filter.hardware',
      value: hardwareName,
    }),
    [hardwareName],
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
            sections={sectionHardware}
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
            filter={filter}
            isTFilterObjectKeys={isTFilterObjectKeys}
          />

          <MemoizedTreeSelectSection
            items={filter.trees}
            handleSelectTree={handleSelectTree}
            selectedTrees={treeIndexes}
          />

          <MemoizedTimeRangeSection
            diffFilter={diffFilter}
            setDiffFilter={setDiffFilter}
          />
        </>
      )}
    </FilterDrawer>
  );
};

export default HardwareDetailsFilter;
