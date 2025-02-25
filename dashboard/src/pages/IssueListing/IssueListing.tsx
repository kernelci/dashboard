import type { ChangeEvent, JSX } from 'react';
import { useCallback } from 'react';

import { useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { z } from 'zod';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';

import { IssueListingPage } from './IssueListingPage';

const IssueListing = (): JSX.Element => {
  const { issueSearch: unsafeIssueSearch } = useSearch({
    strict: false,
  });

  const issueSearch = z.string().catch('').parse(unsafeIssueSearch);

  const navigate = useNavigate({ from: '/issue' });

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          issueSearch: e.target.value,
        }),
      });
    },
    [navigate],
  );

  const { formatMessage } = useIntl();

  return (
    <>
      <MemoizedListingOGTags monitor="/issue" search={issueSearch} />
      <div className="fixed top-0 z-10 mx-[380px] flex w-full pt-5 pr-12 pl-6">
        <div className="flex w-2/3 items-center px-6">
          <DebounceInput
            debouncedSideEffect={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            startingValue={issueSearch}
            placeholder={formatMessage({ id: 'issue.searchPlaceholder' })}
          />
        </div>
      </div>
      <div className="bg-light-gray w-full py-10">
        <IssueListingPage inputFilter={issueSearch} />
      </div>
    </>
  );
};

export default IssueListing;
