//TODO: make this component reusable for TreeDetails and HardwareDetails

import type { Dispatch, SetStateAction } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer from '@/components/Filter/Drawer';
import type {
  TFilter,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';
import { Skeleton } from '@/components/Skeleton';

import { MemoizedCheckboxSection } from '@/components/Tabs/Filters';
import { isTFilterObjectKeys } from '@/types/tree/TreeDetails';

import type { Section } from '@/components/Filter/CheckboxSection';

import { cleanFalseFilters } from './hardwareDetailsUtils';

type TFilterValues = Record<string, boolean>;

interface IHardwareDetailsFilter {
  paramFilter: TFilter;
  hardwareName: string;
  data: THardwareDetails;
}

export const createFilter = (data: THardwareDetails | undefined): TFilter => {
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

    data.builds.items.forEach(b => {
      configs[b.config_name ?? 'Unknown'] = false;
      archs[b.architecture ?? 'Unknown'] = false;
      compilers[b.compiler ?? 'Unknown'] = false;
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

type DiffFilterType = Record<string, Record<string, boolean>>;

const sectionHardware: Section[] = [
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
            setDiffFilter={
              setDiffFilter as Dispatch<SetStateAction<DiffFilterType>>
            }
            diffFilter={diffFilter as DiffFilterType}
            filter={filter as DiffFilterType}
            isTFilterObjectKeys={isTFilterObjectKeys}
          />
        </>
      )}
    </FilterDrawer>
  );
};

export default HardwareDetailsFilter;
