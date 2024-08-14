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
import FilterSummarySection from '@/components/Filter/SummarySection';
import FilterCheckboxSection, {
  ICheckboxSection,
} from '@/components/Filter/CheckboxSection';
import {
  TFilter,
  TFilterKeys,
  TreeDetails as TreeDetailsType,
} from '@/types/tree/TreeDetails';
import { useTreeDetails } from '@/api/TreeDetails';
import { Skeleton } from '@/components/ui/skeleton';

import { cleanFalseFilters } from './treeDetailsUtils';

const zFilterValue = z.record(z.boolean());
type TFilterValues = z.infer<typeof zFilterValue>;

interface ITreeDetailsFilter {
  filter: TFilter;
  treeUrl: string;
  commit: string;
}

const filterFieldMap = {
  git_repository_branch: 'branches',
  config_name: 'configs',
  architecture: 'archs',
  valid: 'status',
} as const satisfies Record<string, TFilterKeys>;

export const mapFilterToReq = (
  filter: TFilter,
): { [key: string]: string[] } => {
  const filterMapped: { [key: string]: string[] } = {};

  Object.entries(filterFieldMap).forEach(([reqField, field]) => {
    const values = filter[field];
    if (!values) return;

    Object.entries(values).forEach(([value, isSelected]) => {
      if (isSelected) {
        if (reqField == 'valid') {
          value = value == 'Success' ? 'true' : 'false';
        }
        if (!filterMapped[reqField]) filterMapped[reqField] = [];
        filterMapped[reqField].push(value);
      }
    });
  });

  return filterMapped;
};

export const createFilter = (data: TreeDetailsType | undefined): TFilter => {
  const status = { Success: false, Failure: false };
  const branches: TFilterValues = {};
  const configs: TFilterValues = {};
  const archs: TFilterValues = {};

  if (data)
    data.builds.forEach(b => {
      if (b.git_repository_branch) branches[b.git_repository_branch] = false;
      if (b.config_name) configs[b.config_name] = false;
      if (b.architecture) archs[b.architecture] = false;
    });

  return { status, branches, configs, archs };
};

const changeFilterValue = (
  filter: TFilter,
  filterField: TFilterKeys,
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

type CheckboxSectionProps = {
  diffFilter: TFilter;
  setDiffFilter: Dispatch<SetStateAction<TFilter>>;
};

// TODO: Remove useState for this forms, use something like react hook forms or tanstack forms (when it gets released)
const CheckboxSection = ({
  diffFilter,
  setDiffFilter,
}: CheckboxSectionProps): JSX.Element => {
  const intl = useIntl();

  const { treeId } = useParams({ from: '/tree/$treeId/' });

  const { data, isLoading } = useTreeDetails(treeId);

  const filter: TFilter = useMemo(() => {
    return createFilter(data);
  }, [data]);

  const parsedFilter: TFilter = useMemo(() => {
    const result = structuredClone(filter);
    Object.keys(result).forEach(key => {
      const currentFilterSection = result[key as TFilterKeys];
      const diffFilterSection = diffFilter[key as TFilterKeys];
      if (diffFilterSection) {
        Object.keys(diffFilterSection).forEach(filterSectionKey => {
          if (currentFilterSection)
            currentFilterSection[filterSectionKey] =
              diffFilterSection[filterSectionKey];
        });
      }
    });

    return result;
  }, [diffFilter, filter]);

  const checkboxSectionsProps: ICheckboxSection[] = useMemo(() => {
    return [
      {
        title: intl.formatMessage({ id: 'global.branch' }),
        subtitle: intl.formatMessage({ id: 'filter.branchSubtitle' }),
        items: parsedFilter.branches,
        onClickItem: (value: string): void => {
          setDiffFilter(old => changeFilterValue(old, 'branches', value));
        },
      },
      {
        title: intl.formatMessage({ id: 'global.status' }),
        subtitle: intl.formatMessage({ id: 'filter.statusSubtitle' }),
        items: parsedFilter.status,
        onClickItem: (value: string): void => {
          setDiffFilter(old => changeFilterValue(old, 'status', value));
        },
      },
      {
        title: intl.formatMessage({ id: 'global.configs' }),
        subtitle: intl.formatMessage({ id: 'filter.configsSubtitle' }),
        items: parsedFilter.configs,
        onClickItem: (value: string): void => {
          setDiffFilter(old => changeFilterValue(old, 'configs', value));
        },
      },
      {
        title: intl.formatMessage({ id: 'global.architecture' }),
        subtitle: intl.formatMessage({ id: 'filter.architectureSubtitle' }),
        items: parsedFilter.archs,
        onClickItem: (value: string): void => {
          setDiffFilter(old => changeFilterValue(old, 'archs', value));
        },
      },
    ];
  }, [
    intl,
    parsedFilter.branches,
    parsedFilter.status,
    parsedFilter.configs,
    parsedFilter.archs,
    setDiffFilter,
  ]);

  if (isLoading)
    return (
      <Skeleton className="grid h-[400px] place-items-center">
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  return (
    <>
      {checkboxSectionsProps.map(props => (
        <DrawerSection key={props.title}>
          <FilterCheckboxSection {...props} />
        </DrawerSection>
      ))}
    </>
  );
};

const MemoizedCheckboxSection = memo(CheckboxSection);

const TreeDetailsFilter = ({
  filter,
  treeUrl,
  commit,
}: ITreeDetailsFilter): JSX.Element => {
  const intl = useIntl();

  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const [diffFilter, setDiffFilter] = useState<TFilter>(filter);

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
    setDiffFilter(filter);
  }, [filter]);

  const handleOpenChange = useCallback(
    (_open: boolean) => {
      setDiffFilter(filter);
    },
    [filter],
  );

  const filterSummaryColumns = useMemo(
    () => [
      { title: intl.formatMessage({ id: 'global.commit' }), value: commit },
    ],
    [intl, commit],
  );

  return (
    <FilterDrawer
      treeURL={treeUrl}
      onFilter={onClickFilterHandle}
      onOpenChange={handleOpenChange}
      onCancel={onClickCancel}
    >
      <DrawerSection hideSeparator>
        <FilterSummarySection
          title={intl.formatMessage({ id: 'global.revision' })}
          columns={filterSummaryColumns}
        />
      </DrawerSection>
      <MemoizedCheckboxSection
        setDiffFilter={setDiffFilter}
        diffFilter={diffFilter}
      />
    </FilterDrawer>
  );
};

export default TreeDetailsFilter;
