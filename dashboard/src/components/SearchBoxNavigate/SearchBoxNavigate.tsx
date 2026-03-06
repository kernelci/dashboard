import { useMatches, useNavigate, useSearch } from '@tanstack/react-router';
import type { ChangeEvent, JSX } from 'react';
import { useCallback, useMemo } from 'react';
import { useIntl } from 'react-intl';
import { HiSearch } from 'react-icons/hi';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import { CustomDialog } from '@/components/Dialog/CustomDialog';

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

    if (['tree', 'treev1', 'treev2'].includes(cleanFullPath)) {
      return 'tree';
    }

    if (['hardware', 'hardwarev1'].includes(cleanFullPath)) {
      return 'hardware';
    }

    if (cleanFullPath === 'issues') {
      return 'issue';
    }

    return 'unknown';
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
      const forwardFields: Record<string, string> = {
        tree: 'treeSearch',
        hardware: 'hardwareSearch',
        issue: 'issueSearch',
      };
      const forwardSearch = { [forwardFields[routeInfo]]: value };

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

  const sharedInput = useMemo(() => {
    return (
      <DebounceInput
        key={`${routeInfo}`}
        debouncedSideEffect={onInputSearchTextChange}
        type="text"
        autoFocus
        startingValue={searchData.currentSearch}
        placeholder={searchData.searchPlaceholder}
      />
    );
  }, [
    onInputSearchTextChange,
    routeInfo,
    searchData.currentSearch,
    searchData.searchPlaceholder,
  ]);

  if (routeInfo === 'unknown') {
    console.error('SearchBoxNavigate shown on an invalid route.');
    console.error('Route is ', matches);
    return <></>;
  }

  return (
    <div className="flex w-full max-w-3xl items-center">
      {/* Mobile: icon button */}
      <CustomDialog
        trigger={
          <button className="min-[475px]:hidden">
            <HiSearch className="size-6" />
          </button>
        }
        content={sharedInput}
        contentClassName="w-9/10 top-10 border-0 bg-transparent p-0 shadow-none min-[475px]:hidden"
        showCloseButton={false}
        showCancel={false}
      />

      {/* Desktop: inline input */}
      <div className="hidden w-full min-[475px]:block">{sharedInput}</div>
    </div>
  );
};
