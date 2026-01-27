import type { ChangeEvent, JSX } from 'react';
import { useCallback } from 'react';

import { useIntl } from 'react-intl';

import { useNavigate, useSearch, Link } from '@tanstack/react-router';

import HardwareListingPage from '@/pages/HardwareNew/HardwareListingPage';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';

const Hardware = (): JSX.Element => {
  const { hardwareSearch } = useSearch({
    from: '/_main/hardware-new',
  });

  const navigate = useNavigate({ from: '/hardware-new' });

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      navigate({
        from: '/hardware-new',
        search: previousSearch => ({
          ...previousSearch,
          hardwareSearch: e.target.value,
        }),
        state: s => s,
      });
    },
    [navigate],
  );

  const { formatMessage } = useIntl();

  return (
    <>
      <MemoizedListingOGTags monitor="/hardware" search={hardwareSearch} />
      <div className="fixed top-0 z-10 mx-[380px] flex w-full pt-5 pr-12 pl-6">
        <div className="flex w-2/3 items-center px-6">
          <DebounceInput
            debouncedSideEffect={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            startingValue={hardwareSearch}
            placeholder={formatMessage({
              id: 'hardware.searchPlaceholder',
            })}
          />
        </div>
      </div>
      <div className="rounded-md bg-green-100 p-3 text-sm text-green-800 dark:bg-green-900 dark:text-green-300">
        This is the new, optimized version of the hardware listing. If you find
        any bugs, please report to{' '}
        <a
          href="https://github.com/kernelci/dashboard/issues"
          target="_blank"
          rel="noreferrer"
          className="underline"
        >
          GitHub Issues
        </a>{' '}
        and you can still access the old version{' '}
        <Link to="/hardware" className="underline">
          here
        </Link>
        . Please note that some historical data might be missing, but it should
        be updated with recent data.
      </div>
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPage inputFilter={hardwareSearch ?? ''} />
      </div>
    </>
  );
};

export default Hardware;
