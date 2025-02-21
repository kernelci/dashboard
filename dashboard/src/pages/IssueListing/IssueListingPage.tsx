import { useMemo, type JSX } from 'react';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

import { Toaster } from '@/components/ui/toaster';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { useIssueListing } from '@/api/issue';
import { IssueTable } from '@/components/IssueTable/IssueTable';
import { matchesRegexOrIncludes } from '@/lib/string';
import type { IssueListingResponse } from '@/types/issueListing';

interface IIssueListingPage {
  inputFilter: string;
}

export const IssueListingPage = ({
  inputFilter,
}: IIssueListingPage): JSX.Element => {
  const { data, status, error, isLoading } = useIssueListing();

  const filteredData = useMemo((): IssueListingResponse => {
    if (!data) {
      return {
        issues: [],
        extras: {},
      };
    }

    return {
      issues: data.issues.filter(issue =>
        matchesRegexOrIncludes(issue.comment, inputFilter),
      ),
      extras: data.extras,
    };
  }, [data, inputFilter]);

  return (
    <QuerySwitcher
      status={status}
      data={data}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
          emptyLabel={'global.error'}
        />
      }
    >
      <Toaster />
      <IssueTable issueListing={filteredData} />
    </QuerySwitcher>
  );
};
