import { useCallback, useMemo, useState } from 'react';
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
} from '@/components/Tabs/Filters';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';
import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';

type TFilterValues = Record<string, boolean>;

interface IHardwareDetailsFilter {
  paramFilter: TFilter;
  hardwareName: string;
  data: THardwareDetails;
}

export const createFilter = (data: THardwareDetails | undefined): TFilter => {
  const buildStatus = { Success: false, Failure: false, Inconclusive: false };

  const bootStatus: TFilterValues = {};
  const testStatus: TFilterValues = {};
  testStatuses.forEach(s => {
    bootStatus[s] = false;
    testStatus[s] = false;
  });

  const configs: TFilterValues = {};
  const archs: TFilterValues = {};
  const compilers: TFilterValues = {};
  const trees: TFilterValues = {};

  if (data) {
    data.trees.forEach(tree => {
      const treeName = tree.treeName ?? 'Unknown';
      const treeBranch = tree.gitRepositoryBranch ?? 'Unknown';

      let treeNameBranch = `${treeName}/${treeBranch}`;

      if (treeName === 'Unknown' && treeBranch === 'Unknown')
        treeNameBranch = 'Unknown';

      trees[treeNameBranch] = false;
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
  }

  return {
    buildStatus,
    configs,
    archs,
    compilers,
    bootStatus,
    testStatus,
    trees,
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
}: IHardwareDetailsFilter): JSX.Element => {
  const isLoading = false;

  const navigate = useNavigate({
    from: '/hardware/$hardwareId/',
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
