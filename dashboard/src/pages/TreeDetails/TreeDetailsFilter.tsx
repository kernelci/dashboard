import {
  Dispatch,
  memo,
  SetStateAction,
  useCallback,
  useMemo,
  useState,
} from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { z } from 'zod';

import { useNavigate, useParams } from '@tanstack/react-router';

import FilterDrawer, { DrawerSection } from '@/components/Filter/Drawer';
import FilterCheckboxSection, {
  ICheckboxSection,
} from '@/components/Filter/CheckboxSection';
import FilterTimeRangeSection from '@/components/Filter/TimeRangeSection';
import {
  TFilter,
  TFilterKeys,
  TFilterObjectsKeys,
  isTFilterObjectKeys,
  TreeDetails as TreeDetailsType,
} from '@/types/tree/TreeDetails';
import { useTreeDetails } from '@/api/TreeDetails';
import { Skeleton } from '@/components/ui/skeleton';

import { cleanFalseFilters } from './treeDetailsUtils';

const zFilterValue = z.record(z.boolean());
type TFilterValues = z.infer<typeof zFilterValue>;

interface ITreeDetailsFilter {
  paramFilter: TFilter;
  treeUrl: string;
}

const filterFieldMap = {
  config_name: 'configs',
  architecture: 'archs',
  compiler: 'compilers',
  valid: 'status',
  'duration_[gte]': 'duration_min',
  'duration_[lte]': 'duration_max',
} as const satisfies Record<string, TFilterKeys>;

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
          if (reqField === 'valid') {
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

export const createFilter = (data: TreeDetailsType | undefined): TFilter => {
  const status = { Success: false, Failure: false };
  const bootStatus = { Success: false, Failure: false };
  const testStatus = { Success: false, Failure: false };
  const configs: TFilterValues = {};
  const archs: TFilterValues = {};
  const compilers: TFilterValues = {};

  if (data)
    data.builds.forEach(b => {
      if (b.config_name) configs[b.config_name] = false;
      if (b.architecture) archs[b.architecture] = false;
      if (b.compiler) compilers[b.compiler] = false;
    });

  return { status, configs, archs, compilers, bootStatus, testStatus };
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
  const filterValue = filterSection?.[value] ?? false;
  filterSection ? (filterSection[value] = !filterValue) : undefined;

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
        items: parsedFilter.status,
        onClickItem: (value: string): void => {
          setDiffFilter(old => changeCheckboxFilterValue(old, 'status', value));
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
    parsedFilter.status,
    parsedFilter.configs,
    parsedFilter.archs,
    parsedFilter.compilers,
    parsedFilter.bootStatus,
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

const TimeRangeSection = ({
  diffFilter,
  setDiffFilter,
}: SectionsProps): JSX.Element => {
  const intl = useIntl();

  const minChangeHandler = useCallback(
    (e: React.FormEvent<HTMLInputElement>) => {
      const value = e.currentTarget.value;
      setDiffFilter(old => ({ ...old, duration_min: parseInt(value) }));
    },
    [setDiffFilter],
  );

  const maxChangeHandler = useCallback(
    (e: React.FormEvent<HTMLInputElement>) => {
      const value = e.currentTarget.value;
      setDiffFilter(old => ({ ...old, duration_max: parseInt(value) }));
    },
    [setDiffFilter],
  );

  return (
    <DrawerSection>
      <FilterTimeRangeSection
        title={intl.formatMessage({ id: 'filter.buildDuration' })}
        subtitle={intl.formatMessage({ id: 'filter.buildDurationSubtitle' })}
        min={diffFilter.duration_min}
        max={diffFilter.duration_max}
        onMaxChange={maxChangeHandler}
        onMinChange={minChangeHandler}
      />
    </DrawerSection>
  );
};

const TreeDetailsFilter = ({
  paramFilter,
  treeUrl,
}: ITreeDetailsFilter): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });

  const { data, isLoading } = useTreeDetails(treeId);

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

  return (
    <FilterDrawer
      treeURL={treeUrl}
      onFilter={onClickFilterHandle}
      onOpenChange={handleOpenChange}
      onCancel={onClickCancel}
    >
      {isLoading ? (
        <Skeleton className="grid h-[400px] place-items-center">
          <FormattedMessage id="global.loading" />
        </Skeleton>
      ) : (
        <>
          <MemoizedCheckboxSection
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
            filter={filter}
          />
          <TimeRangeSection
            setDiffFilter={setDiffFilter}
            diffFilter={diffFilter}
          />
        </>
      )}
    </FilterDrawer>
  );
};

export default TreeDetailsFilter;
