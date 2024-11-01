import {
  Dispatch,
  memo,
  SetStateAction,
  useCallback,
  useMemo,
  useState,
} from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useParams } from '@tanstack/react-router';

import { status as testStatuses } from '@/utils/constants/database';
import FilterDrawer, { DrawerSection } from '@/components/Filter/Drawer';
import FilterCheckboxSection, {
  ICheckboxSection,
} from '@/components/Filter/CheckboxSection';
import FilterTimeRangeSection from '@/components/Filter/TimeRangeSection';
import {
  TFilter,
  TFilterKeys,
  TFilterObjectsKeys,
  TFilterNumberKeys,
  isTFilterObjectKeys,
  BuildsTab as TreeDetailsType,
  TTreeTestsFullData,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';
import { useBuildsTab, useTestsTab } from '@/api/TreeDetails';
import { Skeleton } from '@/components/Skeleton';
import { TRequestFiltersValues } from '@/utils/filters';

import { cleanFalseFilters } from './treeDetailsUtils';

type TFilterValues = Record<string, boolean>;

interface ITreeDetailsFilter {
  paramFilter: TFilter;
  treeUrl: string;
}

const filterFieldMap = {
  'treeDetails.config_name': 'configs',
  'treeDetails.architecture': 'archs',
  'treeDetails.compiler': 'compilers',
  'treeDetails.valid': 'buildStatus',
  'treeDetails.duration_[gte]': 'buildDurationMin',
  'treeDetails.duration_[lte]': 'buildDurationMax',
  'boot.status': 'bootStatus',
  'boot.duration_[gte]': 'bootDurationMin',
  'boot.duration_[lte]': 'bootDurationMax',
  'test.status': 'testStatus',
  'test.duration_[gte]': 'testDurationMin',
  'test.duration_[lte]': 'testDurationMax',
  'test.hardware': 'hardware',
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
      if (b.config_name) configs[b.config_name] = false;
      if (b.architecture) archs[b.architecture] = false;
      if (b.compiler) compilers[b.compiler] = false;
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
      {
        title: intl.formatMessage({ id: 'filter.hardware' }),
        subtitle: intl.formatMessage({ id: 'filter.hardwareSubtitle' }),
        items: parsedFilter.hardware,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, 'hardware', value),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'global.configs' }),
        subtitle: intl.formatMessage({ id: 'filter.configsSubtitle' }),
        items: parsedFilter.configs,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, 'configs', value),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'global.architecture' }),
        subtitle: intl.formatMessage({ id: 'filter.architectureSubtitle' }),
        items: parsedFilter.archs,
        onClickItem: (value: string): void => {
          setDiffFilter(old => changeCheckboxFilterValue(old, 'archs', value));
        },
      },
      {
        title: intl.formatMessage({ id: 'global.compilers' }),
        subtitle: intl.formatMessage({ id: 'filter.compilersSubtitle' }),
        items: parsedFilter.compilers,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, 'compilers', value),
          );
        },
      },
    ];
  }, [
    intl,
    parsedFilter.buildStatus,
    parsedFilter.configs,
    parsedFilter.archs,
    parsedFilter.compilers,
    parsedFilter.bootStatus,
    parsedFilter.testStatus,
    parsedFilter.hardware,
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

const TimeRangeSection = ({
  diffFilter,
  setDiffFilter,
}: SectionsProps): JSX.Element => {
  const intl = useIntl();

  const timeChangeHandler = useCallback(
    (e: React.FormEvent<HTMLInputElement>, field: TFilterNumberKeys) => {
      const value = e.currentTarget.value;
      setDiffFilter(old => ({ ...old, [field]: parseInt(value) }));
    },
    [setDiffFilter],
  );

  const checkboxSectionsProps: React.ComponentProps<
    typeof FilterTimeRangeSection
  >[] = useMemo(
    () => [
      {
        title: intl.formatMessage({ id: 'filter.buildDuration' }),
        subtitle: intl.formatMessage({ id: 'filter.durationSubtitle' }),
        min: diffFilter.buildDurationMin,
        max: diffFilter.buildDurationMax,
        onMaxChange: e => timeChangeHandler(e, 'buildDurationMax'),
        onMinChange: e => timeChangeHandler(e, 'buildDurationMin'),
      },
      {
        title: intl.formatMessage({ id: 'filter.bootDuration' }),
        subtitle: intl.formatMessage({ id: 'filter.durationSubtitle' }),
        min: diffFilter.bootDurationMin,
        max: diffFilter.bootDurationMax,
        onMaxChange: e => timeChangeHandler(e, 'bootDurationMax'),
        onMinChange: e => timeChangeHandler(e, 'bootDurationMin'),
      },
      {
        title: intl.formatMessage({ id: 'filter.testDuration' }),
        subtitle: intl.formatMessage({ id: 'filter.durationSubtitle' }),
        min: diffFilter.testDurationMin,
        max: diffFilter.testDurationMax,
        onMaxChange: e => timeChangeHandler(e, 'testDurationMax'),
        onMinChange: e => timeChangeHandler(e, 'testDurationMin'),
      },
    ],
    [
      diffFilter.bootDurationMax,
      diffFilter.bootDurationMin,
      diffFilter.buildDurationMax,
      diffFilter.buildDurationMin,
      diffFilter.testDurationMax,
      diffFilter.testDurationMin,
      intl,
      timeChangeHandler,
    ],
  );

  return (
    <>
      {checkboxSectionsProps.map(props => (
        <DrawerSection key={props.title}>
          <FilterTimeRangeSection {...props} />
        </DrawerSection>
      ))}
    </>
  );
};

const MemoizedTimeRangeSection = memo(TimeRangeSection);

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

  return (
    <FilterDrawer
      treeURL={treeUrl}
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
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
            filter={filter}
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
