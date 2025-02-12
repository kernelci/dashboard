import type { ChangeEvent } from 'react';
import { useCallback } from 'react';

import { useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import HardwareListingPage from '@/pages/Hardware/HardwareListingPage';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

const Hardware = (): JSX.Element => {
  const { hardwareSearch } = useSearch({
    from: '/hardware',
  });

  const navigate = useNavigate({ from: '/hardware' });

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      navigate({
        from: '/hardware',
        search: previousSearch => ({
          ...previousSearch,
          hardwareSearch: e.target.value,
        }),
      });
    },
    [navigate],
  );

  const intl = useIntl();

  return (
    <>
      <div className="fixed top-0 z-10 mx-[380px] flex w-full pt-5 pr-12 pl-6">
        <div className="flex w-2/3 items-center px-6">
          <DebounceInput
            debouncedSideEffect={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            startingValue={hardwareSearch}
            placeholder={intl.formatMessage({
              id: 'hardware.searchPlaceholder',
            })}
          />
        </div>
      </div>
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPage inputFilter={hardwareSearch ?? ''} />
      </div>
    </>
  );
};

export default Hardware;
