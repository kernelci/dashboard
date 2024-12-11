import { useCallback, useEffect, useMemo, useState } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import type { THardwareDetails } from '@/types/hardware/hardwareDetails';
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

type TFilterValues = Record<string, boolean>;

interface IHardwareDetailsFilter {
  paramFilter: TFilter;
  hardwareName: string;
  data: THardwareDetails;
  selectedTrees?: number[];
}

type TFilterCreate = TFilter & {
  treeIndexes: number[];
};

export const createFilter = (
  data: THardwareDetails | undefined,
): TFilterCreate => {
  const buildStatus = { Success: false, Failure: false, Inconclusive: false };

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
  const trees: TFilterValues = {};
  const treeIndexes: number[] = [];

  if (data) {
    data.trees.forEach(tree => {
      const treeIdx = Number(tree.index);
      const treeName = tree.treeName ?? 'Unknown';
      const treeBranch = tree.gitRepositoryBranch ?? 'Unknown';

      let treeNameBranch = `${treeName}/${treeBranch}`;

      if (treeName === 'Unknown' && treeBranch === 'Unknown')
        treeNameBranch = 'Unknown';

      trees[`${treeNameBranch}__${treeIdx}`] = true;
      treeIndexes.push(treeIdx);
    });

    data.archs.forEach(arch => {
      archs[arch ?? 'Unknown'] = false;
    });
    data.compilers.forEach(compiler => {
      compilers[compiler ?? 'Unknown'] = false;
    });
    data.configs.forEach(config => {
      configs[config ?? 'Unknown'] = false;
    });
    data.builds.issues.forEach(i => (buildIssue[i.id] = false));
    data.boots.issues.forEach(i => (bootIssue[i.id] = false));
    data.tests.issues.forEach(i => (testIssue[i.id] = false));
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
];

const HardwareDetailsFilter = ({
  paramFilter,
  hardwareName,
  data,
  selectedTrees,
}: IHardwareDetailsFilter): JSX.Element => {
  const isLoading = false;

  const navigate = useNavigate({
    from: '/hardware/$hardwareId/',
  });

  const filter: TFilterCreate = useMemo(() => {
    return createFilter(data);
  }, [data]);

  const [diffFilter, setDiffFilter] = useState<TFilter>(paramFilter);
  const [treeIndexes, setTreeIndexes] = useState<number[]>([]);

  useEffect(() => {
    const initialTrees =
      selectedTrees && selectedTrees?.length > 0
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

      if (treeIndexes.includes(idx))
        setTreeIndexes(treeIndexes.filter(i => i !== idx));
      else setTreeIndexes([...treeIndexes, idx]);
    },
    [treeIndexes],
  );

  const drawerLink: IDrawerLink['link'] = useMemo(
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
