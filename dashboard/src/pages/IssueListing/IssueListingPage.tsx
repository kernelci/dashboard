import { useEffect, useMemo, type JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import { Toaster } from '@/components/ui/toaster';

import { useIssueListing } from '@/api/issue';
import { IssueTable } from '@/components/IssueTable/IssueTable';
import { matchesRegexOrIncludes } from '@/lib/string';
import type { IssueListingResponse } from '@/types/issueListing';
import { useSearchStore } from '@/hooks/store/useSearchStore';

import { MemoizedInputTime } from '@/components/InputTime';
import { formattedBreakLineValue } from '@/locales/messages';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

import { mapFilterToReq } from '@/components/Tabs/Filters';

import { MemoizedKcidevFooter } from '@/components/Footer/KcidevFooter';

import IssueListingFilter from './IssueListingFilter';

interface IIssueListingPage {
  inputFilter: string;
}

export const IssueListingPage = ({
  inputFilter,
}: IIssueListingPage): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/issues' });
  const { diffFilter } = searchParams;
  const requestFilters = mapFilterToReq(diffFilter);

  const { data, status, error, isLoading } = useIssueListing(requestFilters);

  const updatePreviousSearch = useSearchStore(s => s.updatePreviousSearch);

  useEffect(
    () => updatePreviousSearch(searchParams),
    [searchParams, updatePreviousSearch],
  );

  const filteredData = useMemo((): IssueListingResponse => {
    if (!data) {
      return {
        issues: [],
        extras: {},
        filters: {
          origins: [],
          culprits: [],
          categories: [],
        },
      };
    }

    return {
      issues: data.issues.filter(issue =>
        matchesRegexOrIncludes(issue.comment, inputFilter),
      ),
      extras: data.extras,
      filters: data.filters,
    };
  }, [data, inputFilter]);

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6 pb-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <span className="text-dim-gray text-left text-sm">
            <FormattedMessage
              id="global.projectUnderDevelopment"
              values={formattedBreakLineValue}
            />
          </span>
          <div className="flex items-center justify-between gap-x-8 gap-y-2 max-[650px]:w-full max-[650px]:flex-wrap max-[650px]:justify-end">
            <MemoizedInputTime
              navigateFrom="/issues"
              defaultInterval={REDUCED_TIME_SEARCH}
            />
            <IssueListingFilter paramFilter={diffFilter} data={data?.filters} />
          </div>
        </div>
        <IssueTable
          issueListing={filteredData}
          status={status}
          queryData={data}
          error={error}
          isLoading={isLoading}
        />
        <MemoizedKcidevFooter commandGroup="issue" />
      </div>
    </>
  );
};
