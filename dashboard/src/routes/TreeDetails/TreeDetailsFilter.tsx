import { useCallback, useMemo } from 'react';
import { useIntl } from 'react-intl';

import FilterDrawer from '@/components/Filter/Drawer';
import FilterSummarySection from '@/components/Filter/SummarySection';
import FilterCheckboxSection, {
  ICheckboxSection,
} from '@/components/Filter/CheckboxSection';
import {
  TreeDetails as TreeDetailsType,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';

interface ITreeDetailsFilter {
  data?: TreeDetailsType;
  onFilter: (filter: TTreeDetailsFilter) => void;
}

type TFilterApplied = { [key: string]: boolean };

const sanitizeData = (
  data: TreeDetailsType | undefined,
): [TFilterApplied, TFilterApplied, TFilterApplied, TFilterApplied, string] => {
  const status = { TRUE: false, FALSE: false };
  const branches: TFilterApplied = {};
  const configs: TFilterApplied = {};
  const archs: TFilterApplied = {};
  let treeUrl = '';

  if (data)
    data.builds.forEach(b => {
      if (b.git_repository_branch) branches[b.git_repository_branch] = false;
      if (b.config_name) configs[b.config_name] = false;
      if (b.architecture) archs[b.architecture] = false;
      if (!treeUrl && b.git_repository_url) treeUrl = b.git_repository_url;
    });

  return [status, branches, configs, archs, treeUrl];
};

const getFilterListFromObj = (filterObj: TFilterApplied): string[] =>
  Object.keys(filterObj).filter(key => filterObj[key]);

const TreeDetailsFilter = ({
  data,
  onFilter,
}: ITreeDetailsFilter): JSX.Element => {
  const intl = useIntl();

  const [statusObj, branchObj, configObj, archObj, treeUrl] = useMemo(
    () => sanitizeData(data),
    [data],
  );

  const onClickFilterHandle = useCallback(() => {
    const filter: TTreeDetailsFilter = {};

    filter.config_name = getFilterListFromObj(configObj);
    filter.git_repository_branch = getFilterListFromObj(branchObj);
    filter.architecture = getFilterListFromObj(archObj);
    filter.valid = getFilterListFromObj(statusObj);

    onFilter(filter);
  }, [onFilter, configObj, branchObj, archObj, statusObj]);

  const checkboxSectionsProps: ICheckboxSection[] = useMemo(() => {
    return [
      {
        title: intl.formatMessage({ id: 'global.branch' }),
        subtitle: intl.formatMessage({ id: 'filter.branchSubtitle' }),
        items: branchObj,
        onClickItem: (branch: string, isChecked: boolean) =>
          (branchObj[branch] = isChecked),
      },
      {
        title: intl.formatMessage({ id: 'global.status' }),
        subtitle: intl.formatMessage({ id: 'filter.statusSubtitle' }),
        items: Object.keys(statusObj).reduce((acc, k) => {
          const newKey = k == 'TRUE' ? 'valid' : 'invalid';
          acc[newKey] = statusObj[k];
          return acc;
        }, {} as TFilterApplied),
        onClickItem: (status: string, isChecked: boolean) =>
          (statusObj[status == 'valid' ? 'TRUE' : 'FALSE'] = isChecked),
      },
      {
        title: intl.formatMessage({ id: 'global.configs' }),
        subtitle: intl.formatMessage({ id: 'filter.configsSubtitle' }),
        items: configObj,
        onClickItem: (config: string, isChecked: boolean) =>
          (configObj[config] = isChecked),
      },
      {
        title: intl.formatMessage({ id: 'global.architecture' }),
        subtitle: intl.formatMessage({ id: 'filter.architectureSubtitle' }),
        items: archObj,
        onClickItem: (arch: string, isChecked: boolean) =>
          (archObj[arch] = isChecked),
      },
    ];
  }, [statusObj, branchObj, configObj, archObj, intl]);

  const checkboxSectionsComponents = useMemo(
    () =>
      checkboxSectionsProps.map(props => (
        <FilterCheckboxSection key={props.title} {...props} />
      )),
    [checkboxSectionsProps],
  );

  return (
    <FilterDrawer treeURL={treeUrl} onFilter={onClickFilterHandle}>
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
    { title: 'Matainer', value: '' },
    { title: 'Estimate to complete', value: '' },
    {
      title: 'Commit/tag',
      value: '5.15.150-rc1 - 3ab4d9c9e190217ee7e974c70b96795cd2f74611',
    },
  ],
};
