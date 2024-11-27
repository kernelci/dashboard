import type { Dispatch, SetStateAction } from 'react';
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

// TODO: We can improve this idea and replace mapFilterToReq entirely
export const mapFilterToReq = (filter: TFilter): TFilter => {
  const filterMapped: { [key: string]: string[] } = {};

  Object.entries(filterFieldMap).forEach(([reqField, field]) => {
    const values = filter[field as TFilterKeys];
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
}

// TODO: Remove useState for this forms, use something like react hook forms or tanstack forms (when it gets released)
const CheckboxSection = ({
  diffFilter,
  setDiffFilter,
  filter,
  isTFilterObjectKeys,
  sections,
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
        onClickItem: (value: string): void => {
          setDiffFilter(old =>
            changeCheckboxFilterValue(old, section.sectionKey, value),
          );
        },
      })),
    [intl, parsedFilter, sections, setDiffFilter],
  );

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
