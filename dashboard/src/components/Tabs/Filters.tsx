import type { Dispatch, SetStateAction, JSX } from 'react';
import { memo, useCallback, useMemo } from 'react';
import { useIntl } from 'react-intl';

import type {
  ICheckboxSection,
  ISectionItem,
} from '@/components/Filter/CheckboxSection';
import FilterCheckboxSection from '@/components/Filter/CheckboxSection';

import FilterTimeRangeSection from '@/components/Filter/TimeRangeSection';

import { DrawerSection } from '@/components/Filter/Drawer';

import type {
  TFilterKeys,
  TFilter,
  TFilterObjectsKeys,
  TFilterNumberKeys,
} from '@/types/general';
import { filterFieldMap, zFilterObjectsKeys } from '@/types/general';
import { UNCATEGORIZED_STRING } from '@/utils/constants/backend';
import { version_prefix } from '@/utils/utils';

export const NO_VALID_INDEX = -1;

// TODO: We can improve this idea and replace mapFilterToReq entirely
export const mapFilterToReq = (filter: TFilter): TFilter => {
  const filterMapped: { [key: string]: string[] } = {};

  Object.entries(filterFieldMap).forEach(([reqField, field]) => {
    const values = filter[field as TFilterKeys];
    if (!values) {
      return;
    }

    if (typeof values === 'object') {
      Object.entries(values).forEach(([value, isSelected]) => {
        if (isSelected) {
          if (
            reqField === 'treeDetails.valid' ||
            reqField === 'hardwareDetails.valid'
          ) {
            if (value === 'Success') {
              value = 'true';
            } else if (value === 'Failed') {
              value = 'false';
            } else {
              value = 'none';
            }
          }

          if (!filterMapped[reqField]) {
            filterMapped[reqField] = [];
          }

          if (reqField.endsWith('issue')) {
            // combines the issue filter itself as "<issue_id>,<issue_version>"
            let issue_id = UNCATEGORIZED_STRING;
            let issue_version = null;

            if (value !== UNCATEGORIZED_STRING) {
              const split_issue_data = value.split(` ${version_prefix}`);
              issue_version = split_issue_data.pop();
              issue_id = split_issue_data.join(` ${version_prefix}`);
            }

            value = `${issue_id},${issue_version}`;
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

const parseCheckboxFilter = (
  filter: TFilter,
  diffFilter: TFilter,
  isTFilterObjectKeys: (key: string) => boolean,
): TFilter => {
  const result: TFilter = structuredClone(filter);

  Object.keys(result).forEach(key => {
    // key is always returned as string in Object.keys function, but he is a TFilterObjectKeys type.
    const validateKey = zFilterObjectsKeys.catch('buildStatus').parse(key);
    const currentFilterSection = result[validateKey];

    if (!currentFilterSection || !isTFilterObjectKeys(validateKey)) {
      return;
    }

    const diffFilterSection = diffFilter[validateKey];

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
  const newFilter = JSON.parse(JSON.stringify(filter ?? {}));
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
  isTFilterObjectKeys: (key: string) => boolean;
  sections: ISectionItem[];
  showAllIcons?: boolean;
}

interface ITreeSectionProps {
  items?: Record<string, boolean>;
  selectedTrees?: number[];
  handleSelectTree: (index: string) => void;
  showIcon?: boolean;
}

// TODO: Remove useState for this forms, use something like react hook forms or tanstack forms (when it gets released)
const CheckboxSection = ({
  diffFilter,
  setDiffFilter,
  filter,
  isTFilterObjectKeys,
  sections,
  showAllIcons = true,
}: ICheckboxSectionProps): JSX.Element => {
  const intl = useIntl();

  const parsedFilter = useMemo(
    () => parseCheckboxFilter(filter, diffFilter, isTFilterObjectKeys),
    [diffFilter, filter, isTFilterObjectKeys],
  );

  const checkboxSectionsProps: ICheckboxSection[] = useMemo(
    () =>
      sections.map(section => ({
        title: intl.formatMessage({ id: section.title }),
        subtitle: intl.formatMessage({ id: section.subtitle }),
        items: parsedFilter[section.sectionKey],
        isGlobal: section.isGlobal,
        showIcon: showAllIcons,
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, section.sectionKey, value),
          );
        },
      })),
    [intl, parsedFilter, sections, setDiffFilter, showAllIcons],
  );

  return (
    <>
      {checkboxSectionsProps.map(
        (props, i) =>
          Object.entries(props.items ?? {}).length > 0 && (
            <DrawerSection key={props.title} hideSeparator={i === 0}>
              <FilterCheckboxSection {...props} />
            </DrawerSection>
          ),
      )}
    </>
  );
};

export const MemoizedCheckboxSection = memo(CheckboxSection);

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

export const MemoizedTimeRangeSection = memo(TimeRangeSection);

const TreeSelectSection = ({
  items,
  handleSelectTree,
  selectedTrees,
  showIcon = true,
}: ITreeSectionProps): JSX.Element => {
  const intl = useIntl();

  const filterItems = useMemo(() => {
    if (!items) {
      return {};
    }

    const filteredItems: Record<string, boolean> = {};

    Object.keys(items).map(key => {
      const idx = Number(key.split('__')[1] ?? NO_VALID_INDEX);

      filteredItems[key] = selectedTrees?.includes(idx) || false;
    });

    return filteredItems;
  }, [items, selectedTrees]);

  return (
    <DrawerSection key="Tree">
      <FilterCheckboxSection
        title={intl.formatMessage({ id: 'global.trees' })}
        items={filterItems}
        isGlobal
        subtitle={intl.formatMessage({ id: 'filter.treeSubtitle' })}
        onClickItem={handleSelectTree}
        showIcon={showIcon}
      />
    </DrawerSection>
  );
};

export const MemoizedTreeSelectSection = memo(TreeSelectSection);
