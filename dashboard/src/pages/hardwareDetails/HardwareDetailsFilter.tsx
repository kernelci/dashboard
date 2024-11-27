//TODO: make this component reusable for TreeDetails and HardwareDetails

import type { Dispatch, SetStateAction } from 'react';
import { memo, useCallback, useMemo, useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import type { IDrawerLink } from '@/components/Filter/Drawer';
import FilterDrawer, { DrawerSection } from '@/components/Filter/Drawer';
import type { ICheckboxSection } from '@/components/Filter/CheckboxSection';
import FilterCheckboxSection from '@/components/Filter/CheckboxSection';
import type {
  TFilter,
  TFilterKeys,
  TFilterObjectsKeys,
  THardwareDetails,
  TRequestFiltersValues,
} from '@/types/hardware/hardwareDetails';
import { isTFilterObjectKeys } from '@/types/hardware/hardwareDetails';
import { Skeleton } from '@/components/Skeleton';

import { cleanFalseFilters } from './hardwareDetailsUtils';

type TFilterValues = Record<string, boolean>;

interface IHardwareDetailsFilter {
  paramFilter: TFilter;
  hardwareName: string;
  data: THardwareDetails;
}

const filterFieldMap = {
  'hardwareDetails.config_name': 'configs',
  'hardwareDetails.architecture': 'archs',
  'hardwareDetails.compiler': 'compilers',
  'hardwareDetails.valid': 'buildStatus',
  'hardwareDetails.duration_[gte]': 'buildDurationMin',
  'hardwareDetails.duration_[lte]': 'buildDurationMax',
  'hardwareDetails.trees': 'trees',
  'boot.status': 'bootStatus',
  'boot.duration_[gte]': 'bootDurationMin',
  'boot.duration_[lte]': 'bootDurationMax',
  'test.status': 'testStatus',
  'test.duration_[gte]': 'testDurationMin',
  'test.duration_[lte]': 'testDurationMax',
  'test.path': 'testPath',
  'boot.path': 'bootPath',
} as const satisfies Record<TRequestFiltersValues, TFilterKeys>;

export const mapFilterToReq = (
  filter: TFilter,
): { [key: string]: string[] } => {
  const filterMapped: { [key: string]: string[] } = {};

  Object.entries(filterFieldMap).forEach(([reqField, field]) => {
    const values = filter[field];
    if (!values) return;

    if (typeof values === 'object') {
      Object.entries(values).forEach(([value, isSelected]) => {
        if (isSelected) {
          if (reqField === 'treeDetails.valid') {
            value = value === 'Success' ? 'true' : 'false';
          }
          if (!filterMapped[reqField]) {
            filterMapped[reqField] = [];
          }
          filterMapped[reqField].push(value);
        }
      });
    } else {
      filterMapped[reqField] = [values.toString()];
    }
  });
  return filterMapped;
};

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

const parseCheckboxFilter = (filter: TFilter, diffFilter: TFilter): TFilter => {
  const result = structuredClone(filter);
  Object.keys(result).forEach(key => {
    const currentFilterSection = result[key as TFilterObjectsKeys];

    if (!currentFilterSection || !isTFilterObjectKeys(key)) {
      return;
    }

    const diffFilterSection = diffFilter[key];

    if (diffFilterSection) {
      Object.keys(diffFilterSection).forEach(filterSectionKey => {
        currentFilterSection[filterSectionKey] =
          diffFilterSection[filterSectionKey];
      });
    }
  });

  return result;
};

const changeCheckboxFilterValue = (
  filter: TFilter,
  filterField: TFilterObjectsKeys,
  value: string,
): TFilter => {
  const newFilter: TFilter = JSON.parse(JSON.stringify(filter ?? {}));
  if (!newFilter[filterField]) {
    newFilter[filterField] = {};
  }
  const filterSection = newFilter[filterField];
  const filterValue = filterSection[value] ?? false;
  filterSection[value] = !filterValue;

  return newFilter;
};

type SectionsProps = {
  diffFilter: TFilter;
  setDiffFilter: Dispatch<SetStateAction<TFilter>>;
};

interface ICheckboxSectionProps extends SectionsProps {
  filter: TFilter;
}

// TODO: Remove useState for this forms, use something like react hook forms or tanstack forms (when it gets released)
const CheckboxSection = ({
  diffFilter,
  setDiffFilter,
  filter,
}: ICheckboxSectionProps): JSX.Element => {
  const intl = useIntl();

  const parsedFilter: TFilter = useMemo(
    () => parseCheckboxFilter(filter, diffFilter),
    [diffFilter, filter],
  );

  const checkboxSectionsProps: ICheckboxSection[] = useMemo(() => {
    return [
      {
        title: intl.formatMessage({ id: 'filter.buildStatus' }),
        subtitle: intl.formatMessage({ id: 'filter.statusSubtitle' }),
        items: parsedFilter.buildStatus,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, 'buildStatus', value),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'filter.bootStatus' }),
        subtitle: intl.formatMessage({ id: 'filter.statusSubtitle' }),
        items: parsedFilter.bootStatus,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, 'bootStatus', value),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'filter.testStatus' }),
        subtitle: intl.formatMessage({ id: 'filter.statusSubtitle' }),
        items: parsedFilter.testStatus,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, 'testStatus', value),
          );
        },
      },
    ];
  }, [
    intl,
    parsedFilter.bootStatus,
    parsedFilter.buildStatus,
    parsedFilter.testStatus,
    setDiffFilter,
  ]);

  return (
    <>
      {checkboxSectionsProps.map((props, i) => (
        <DrawerSection key={props.title} hideSeparator={i === 0}>
          <FilterCheckboxSection {...props} />
        </DrawerSection>
      ))}
    </>
  );
};

const MemoizedCheckboxSection = memo(CheckboxSection);

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
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
            filter={filter}
          />
        </>
      )}
    </FilterDrawer>
  );
};

export default HardwareDetailsFilter;
