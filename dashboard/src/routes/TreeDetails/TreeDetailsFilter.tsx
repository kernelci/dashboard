import { useCallback, useMemo, useState } from 'react';
import { useIntl } from 'react-intl';

import FilterDrawer from '@/components/Filter/Drawer';
import FilterSummarySection from '@/components/Filter/SummarySection';
import FilterCheckboxSection, {
  ICheckboxSection,
} from '@/components/Filter/CheckboxSection';
import { TreeDetails as TreeDetailsType } from '@/types/tree/TreeDetails';

type TFilterValues = { [key: string]: boolean };
export type TFilter =
  | { [key in TFilterKeys]: TFilterValues }
  | Record<string, never>;

interface ITreeDetailsFilter {
  filter: TFilter;
  onFilter: (filter: TFilter) => void;
  treeUrl: string;
}

export type TFilterKeys = (typeof filterFieldMap)[keyof typeof filterFieldMap];

const filterFieldMap = {
  git_repository_branch: 'branches',
  config_name: 'configs',
  architecture: 'archs',
  valid: 'status',
} as const;

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
          value = value == 'Sucess' ? 'true' : 'false';
        }
        if (!filterMapped[reqField]) filterMapped[reqField] = [];
        filterMapped[reqField].push(value);
      }
    });
  });

  return filterMapped;
};

export const createFilter = (data: TreeDetailsType | undefined): TFilter => {
  const status = { Sucess: false, Failure: false };
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
  isSelected: boolean,
): TFilter => {
  const newFilter = { ...filter };
  if (newFilter[filterField]) {
    newFilter[filterField][value] = isSelected;
  } else {
    newFilter[filterField] = {
      [value]: isSelected,
    };
  }

  return newFilter;
};

const TreeDetailsFilter = ({
  filter,
  onFilter,
  treeUrl,
}: ITreeDetailsFilter): JSX.Element => {
  const intl = useIntl();
  const [diffFilter, setDiffFilter] = useState<TFilter>({});

  const onClickFilterHandle = useCallback(() => {
    const newFilter = { ...filter };
    Object.entries(diffFilter).forEach(([key, value]) => {
      const typedKey = key as keyof typeof diffFilter;

      newFilter[typedKey] = {
        ...newFilter[typedKey],
        ...value,
      };
    });

    onFilter(newFilter);
    setDiffFilter({});
  }, [filter, diffFilter, onFilter]);

  const onClickCancel = useCallback(() => {
    setDiffFilter({});
  }, []);

  const checkboxSectionsProps: ICheckboxSection[] = useMemo(() => {
    return [
      {
        title: intl.formatMessage({ id: 'global.branch' }),
        subtitle: intl.formatMessage({ id: 'filter.branchSubtitle' }),
        items: filter.branches,
        onClickItem: (value: string, isChecked: boolean): void => {
          setDiffFilter(old =>
            changeFilterValue(old, 'branches', value, isChecked),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'global.status' }),
        subtitle: intl.formatMessage({ id: 'filter.statusSubtitle' }),
        items: filter.status,
        onClickItem: (value: string, isChecked: boolean): void => {
          setDiffFilter(old =>
            changeFilterValue(old, 'status', value, isChecked),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'global.configs' }),
        subtitle: intl.formatMessage({ id: 'filter.configsSubtitle' }),
        items: filter.configs,
        onClickItem: (value: string, isChecked: boolean): void => {
          setDiffFilter(old =>
            changeFilterValue(old, 'configs', value, isChecked),
          );
        },
      },
      {
        title: intl.formatMessage({ id: 'global.architecture' }),
        subtitle: intl.formatMessage({ id: 'filter.architectureSubtitle' }),
        items: filter.archs,
        onClickItem: (value: string, isChecked: boolean): void => {
          setDiffFilter(old =>
            changeFilterValue(old, 'archs', value, isChecked),
          );
        },
      },
    ];
  }, [intl, filter]);

  const checkboxSectionsComponents = useMemo(
    () =>
      checkboxSectionsProps.map(props => (
        <FilterCheckboxSection key={props.title} {...props} />
      )),
    [checkboxSectionsProps],
  );

  return (
    <FilterDrawer
      treeURL={treeUrl}
      onFilter={onClickFilterHandle}
      onCancel={onClickCancel}
    >
      <FilterSummarySection {...summarySectionProps} />
      {checkboxSectionsComponents}
    </FilterDrawer>
  );
};

export default TreeDetailsFilter;

const summarySectionProps = {
  title: 'Tree',
  columns: [
    { title: 'Tree', value: 'stable-rc' },
    {
      title: 'Commit/tag',
      value: '5.15.150-rc1 - 3ab4d9c9e190217ee7e974c70b96795cd2f74611',
    },
  ],
};
