import { useCallback, useMemo, useState, type JSX } from 'react';

import { useNavigate } from '@tanstack/react-router';

import FilterDrawer from '@/components/Filter/Drawer';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';

import { MemoizedCheckboxSection } from '@/components/Tabs/Filters';

import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import type { IssueListingFilters } from '@/types/issueListing';
import { OptionFilters } from '@/types/filters';

type PossibleIssueListingFilters = Partial<
  Pick<
    TFilter,
    'origins' | 'issueCategories' | 'issueCulprits' | 'issueOptions'
  >
>;

export const createFilter = (
  data: IssueListingFilters,
): PossibleIssueListingFilters => {
  const filters: PossibleIssueListingFilters = {};

  filters.origins = {};
  filters.issueCulprits = {};
  filters.issueOptions = {};
  filters.issueCategories = {};

  const IssueListingOptionFilters = Object.keys(OptionFilters['issueListing']);
  for (let i = 0; i < IssueListingOptionFilters.length; i += 1) {
    const option = IssueListingOptionFilters[i];
    filters.issueOptions[option] = false;
  }

  for (const origin of data.origins) {
    // TODO: remove this origin exception once the culprit filter is available.
    // This origin is from a single unique issue where the culprit is not code;
    // while the culprit filter is hardcoded as "code" in the frontend,
    // this origin will also be ignored.
    // Trying to filter by this origin with culprit code will return 0 results, so while
    // the culprit filter is always 'code' the user doesn't need to see this origin option.
    if (origin !== '_') {
      filters.origins[origin] = false;
    }
  }

  for (const culprit of data.culprits) {
    filters.issueCulprits[culprit] = false;
  }

  for (const category of data.categories) {
    filters.issueCategories[category] = false;
  }

  return filters;
};

const sectionTrees: ISectionItem[] = [
  {
    title: 'filter.origins',
    subtitle: 'filter.originsSubtitle',
    sectionKey: 'origins',
  },
  {
    title: 'filter.issueCategories',
    subtitle: 'filter.issueCategoriesSubtitle',
    sectionKey: 'issueCategories',
  },
  //// These sections will be available to the user once the data is stable in kcidb
  // {
  //   title: 'filter.issueCulprit',
  //   subtitle: 'filter.issueCulpritSubtitle',
  //   sectionKey: 'issueCulprits',
  // },
  // {
  //   title: 'filter.options',
  //   subtitle: 'filter.optionsSubtitle',
  //   sectionKey: 'issueOptions',
  // },
];

const IssueListingFilter = ({
  paramFilter,
  data,
}: {
  paramFilter: TFilter;
  data?: IssueListingFilters;
}): JSX.Element => {
  const navigate = useNavigate({
    from: '/issues',
  });

  const filter: TFilter = useMemo(() => {
    if (!data) {
      return {};
    }

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
      state: s => s,
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
      onFilter={onClickFilterHandle}
      onOpenChange={handleOpenChange}
      onCancel={onClickCancel}
      showLegend={false}
    >
      <MemoizedCheckboxSection
        sections={sectionTrees}
        setDiffFilter={setDiffFilter}
        diffFilter={diffFilter}
        filter={filter}
        isTFilterObjectKeys={isTFilterObjectKeys}
        showAllIcons={false}
      />
    </FilterDrawer>
  );
};

export default IssueListingFilter;
