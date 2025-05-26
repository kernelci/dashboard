import { useCallback, useMemo, useState, type JSX } from 'react';

import { useNavigate } from '@tanstack/react-router';

import FilterDrawer from '@/components/Filter/Drawer';
import type { ISectionItem } from '@/components/Filter/CheckboxSection';

import { MemoizedCheckboxSection } from '@/components/Tabs/Filters';

import { isTFilterObjectKeys, type TFilter } from '@/types/general';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import type { IssueListingItem } from '@/types/issueListing';
import { OptionFilters } from '@/types/filters';
import {
  CULPRIT_CODE,
  CULPRIT_HARNESS,
  CULPRIT_TOOL,
} from '@/utils/constants/issues';

type PossibleIssueListingFilters = Partial<
  Pick<
    TFilter,
    'origins' | 'issueCategories' | 'issueCulprits' | 'issueOptions'
  >
>;

export const createFilter = (
  data: IssueListingItem[] | undefined,
): PossibleIssueListingFilters => {
  const filters: PossibleIssueListingFilters = {};

  const IssueListingOptionFilters = Object.keys(OptionFilters['issueListing']);

  if (data) {
    filters.origins = {};
    filters.issueCulprits = {};
    filters.issueOptions = {};
    filters.issueCategories = {};

    for (let i = 0; i < IssueListingOptionFilters.length; i += 1) {
      const option = IssueListingOptionFilters[i];
      filters.issueOptions[option] = false;
    }

    for (let i = 0; i < data.length; i += 1) {
      const issue = data[i];
      filters.origins[issue.origin] = false;

      if (issue.culprit_code) {
        filters.issueCulprits[CULPRIT_CODE] = false;
      }
      if (issue.culprit_harness) {
        filters.issueCulprits[CULPRIT_HARNESS] = false;
      }
      if (issue.culprit_tool) {
        filters.issueCulprits[CULPRIT_TOOL] = false;
      }

      if (issue.categories) {
        for (let j = 0; j < issue.categories.length; j += 1) {
          const category = issue.categories[j];
          filters.issueCategories[category] = false;
        }
      }
    }
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
  data?: IssueListingItem[];
}): JSX.Element => {
  const navigate = useNavigate({
    from: '/issues',
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
