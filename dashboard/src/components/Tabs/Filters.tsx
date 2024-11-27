import type { Dispatch, SetStateAction } from 'react';
import { memo, useCallback, useMemo } from 'react';
import { useIntl } from 'react-intl';

import type {
  ICheckboxSection,
  Section,
} from '@/components/Filter/CheckboxSection';
import FilterCheckboxSection from '@/components/Filter/CheckboxSection';

import FilterTimeRangeSection from '@/components/Filter/TimeRangeSection';

import { DrawerSection } from '../Filter/Drawer';

import type { RecordDiffType } from './tabsUtils';

export const mapFilterToReq = <T extends Record<string, string>>(
  filter: T,
  fieldMap: Record<string, string>,
): { [key: string]: string[] } => {
  const filterMapped: { [key: string]: string[] } = {};

  Object.entries(fieldMap).forEach(([reqField, field]) => {
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

const parseCheckboxFilter = <T extends Record<string, Record<string, boolean>>>(
  filter: T,
  diffFilter: T,
  isTFilterObjectKeys: (key: string) => boolean,
): T => {
  const result = structuredClone(filter) as T;
  Object.keys(result).forEach(key => {
    const currentFilterSection = result[key];

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

const changeCheckboxFilterValue = <
  T extends Record<string, Record<string, boolean>>,
  K extends keyof T,
>(
  filter: T,
  filterField: K,
  value: string,
): T => {
  const newFilter: T = JSON.parse(JSON.stringify(filter ?? {}));
  if (!newFilter[filterField]) {
    newFilter[filterField] = {} as T[K];
  }

  const filterSection = newFilter[filterField] as Record<string, boolean>;
  const filterValue = filterSection[value] ?? false;
  filterSection[value] = !filterValue;

  return newFilter;
};

type SectionsProps<T extends RecordDiffType> = {
  diffFilter: T;
  setDiffFilter: Dispatch<SetStateAction<T>>;
};

interface ICheckboxSectionProps<
  T extends Record<string, Record<string, boolean>>,
> extends SectionsProps<T> {
  filter: T;
  isTFilterObjectKeys: (key: string) => boolean;
  sections: Section[];
  //getSections: (parsedFilter: T) => ICheckboxSection[];
}

// TODO: Remove useState for this forms, use something like react hook forms or tanstack forms (when it gets released)
const CheckboxSection = <T extends Record<string, Record<string, boolean>>>({
  diffFilter,
  setDiffFilter,
  filter,
  isTFilterObjectKeys,
  sections,
}: ICheckboxSectionProps<T>): JSX.Element => {
  const intl = useIntl();

  const parsedFilter: T = useMemo(
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

const TimeRangeSection = <T extends Record<string, number>, K extends string>({
  diffFilter,
  setDiffFilter,
}: SectionsProps<T>): JSX.Element => {
  const intl = useIntl();

  const timeChangeHandler = useCallback(
    (e: React.FormEvent<HTMLInputElement>, field: K) => {
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
        onMaxChange: e => timeChangeHandler(e, 'buildDurationMax' as K),
        onMinChange: e => timeChangeHandler(e, 'buildDurationMin' as K),
      },
      {
        title: intl.formatMessage({ id: 'filter.bootDuration' }),
        subtitle: intl.formatMessage({ id: 'filter.durationSubtitle' }),
        min: diffFilter.bootDurationMin,
        max: diffFilter.bootDurationMax,
        onMaxChange: e => timeChangeHandler(e, 'bootDurationMax' as K),
        onMinChange: e => timeChangeHandler(e, 'bootDurationMin' as K),
      },
      {
        title: intl.formatMessage({ id: 'filter.testDuration' }),
        subtitle: intl.formatMessage({ id: 'filter.durationSubtitle' }),
        min: diffFilter.testDurationMin,
        max: diffFilter.testDurationMax,
        onMaxChange: e => timeChangeHandler(e, 'testDurationMax' as K),
        onMinChange: e => timeChangeHandler(e, 'testDurationMin' as K),
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
