import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import { z } from 'zod';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';

import { IssueListingPage } from './IssueListingPage';

const IssueListing = (): JSX.Element => {
  const { issueSearch: unsafeIssueSearch } = useSearch({
    strict: false,
  });

  const issueSearch = z.string().catch('').parse(unsafeIssueSearch);

  return (
    <>
      <MemoizedListingOGTags monitor="/issues" search={issueSearch} />
      <div className="bg-light-gray w-full py-10">
        <IssueListingPage inputFilter={issueSearch} />
      </div>
    </>
  );
};

export default IssueListing;
