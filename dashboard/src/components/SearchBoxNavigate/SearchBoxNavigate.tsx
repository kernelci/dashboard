import { useMatches, useNavigate, useSearch } from '@tanstack/react-router';
import type { ChangeEvent, JSX } from 'react';
import { useCallback, useMemo } from 'react';
import { useIntl } from 'react-intl';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

interface ISearchData {
  currentSearch?: string;
  searchPlaceholder: string;
  navigateTarget: string;
}

export const SearchBoxNavigate = (): JSX.Element => {
  const matches = useMatches();
  const routeInfo = useMemo(() => {
    const lastMatch = matches[matches.length - 1];
    const cleanFullPath = lastMatch?.fullPath.replace(/\//g, '') ?? '';

    const isTreeListing = ['tree', 'treev1', 'treev2'].includes(cleanFullPath);
    const isHardwareListing = ['hardware', 'hardwarev1'].includes(
      cleanFullPath,
    );
    const isIssueListing = cleanFullPath === 'issues';

    return isTreeListing
      ? 'tree'
      : isHardwareListing
        ? 'hardware'
        : isIssueListing
          ? 'issue'
          : 'unknown';
  }, [matches]);
  const { formatMessage } = useIntl();

  const { treeSearch, hardwareSearch, issueSearch } = useSearch({
    strict: false,
  });
  const searchData = useMemo((): ISearchData => {
    switch (routeInfo) {
      case 'tree':
        return {
          currentSearch: treeSearch,
          searchPlaceholder: formatMessage({ id: 'tree.searchPlaceholder' }),
          navigateTarget: 'treeSearch',
        };
      case 'hardware':
        return {
          currentSearch: hardwareSearch,
          searchPlaceholder: formatMessage({
            id: 'hardware.searchPlaceholder',
          }),
          navigateTarget: 'hardwareSearch',
        };
      case 'issue':
        return {
          currentSearch: issueSearch,
          searchPlaceholder: formatMessage({
            id: 'issue.searchPlaceholder',
          }),
          navigateTarget: 'issueSearch',
        };
      default:
        return {
          currentSearch: '',
          searchPlaceholder: '',
          navigateTarget: '',
        };
    }
  }, [routeInfo, treeSearch, formatMessage, hardwareSearch, issueSearch]);

  const navigate = useNavigate();

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      // using routeInfo as a dependency instead of searchData so that we don't depend on useSearch
      let forwardSearch = {};
      switch (routeInfo) {
        case 'tree':
          forwardSearch = { treeSearch: value };
          break;
        case 'hardware':
          forwardSearch = { hardwareSearch: value };
          break;
        case 'issue':
          forwardSearch = { issueSearch: value };
          break;
        default:
          break;
      }
      navigate({
        to: '.',
        search: previousSearch => ({
          ...previousSearch,
          ...forwardSearch,
        }),
      });
    },
    [navigate, routeInfo],
  );

  if (routeInfo === 'unknown') {
    console.error('SearchBoxNavigate shown on an invalid route.');
    console.error('Route is ', matches);
    return <></>;
  }

  return (
    <div className="fixed top-0 z-10 mx-[380px] flex w-full pt-5 pr-12 pl-6">
      <div className="flex w-2/3 items-center px-6">
        <DebounceInput
          key={routeInfo}
          debouncedSideEffect={onInputSearchTextChange}
          className="w-2/3"
          type="text"
          startingValue={searchData.currentSearch}
          placeholder={searchData.searchPlaceholder}
        />
      </div>
    </div>
  );
};
