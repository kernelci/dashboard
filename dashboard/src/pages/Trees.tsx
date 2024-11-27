import type { ChangeEvent } from 'react';
import { useCallback } from 'react';

import { useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { z } from 'zod';

import TreeListingPage from '@/components/TreeListingPage/TreeListingPage';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

const Trees = (): JSX.Element => {
  const { treeSearch: unsafeTreeSearch } = useSearch({
    strict: false,
  });

  const treeSearch = z.string().catch('').parse(unsafeTreeSearch);

  const navigate = useNavigate({ from: '/' });

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          treeSearch: e.target.value,
        }),
      });
    },
    [navigate],
  );

  const intl = useIntl();

  return (
    <>
      <div className="w-full bg-lightGray py-10">
        <TreeListingPage inputFilter={treeSearch} />
      </div>
      <div className="fixed top-0 z-10 mx-[380px] flex w-full pl-6 pr-12 pt-5">
        <div className="flex w-2/3 items-center px-6">
          <DebounceInput
            debouncedSideEffect={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            startingValue={treeSearch}
            placeholder={intl.formatMessage({ id: 'tree.searchPlaceholder' })}
          />
        </div>
      </div>
    </>
  );
};

export default Trees;
