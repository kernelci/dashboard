import type { ChangeEvent, JSX } from 'react';
import { useCallback } from 'react';

import { useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import HardwareListingPageV2 from '@/pages/Hardware/HardwareListingPageV2';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import { NewPageBanner } from '@/components/Banner/PageBanner';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

export const HardwareV2 = ({
  urlFromMap,
}: {
  urlFromMap: HardwareListingRoutesMap['v2'];
}): JSX.Element => {
  const { hardwareListingVersion } = useFeatureFlag();
  const { hardwareSearch } = useSearch({
    from: urlFromMap.search,
  });

  const navigate = useNavigate({ from: urlFromMap.navigate });

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      navigate({
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
      {hardwareListingVersion !== 'v2' && (
        <NewPageBanner
          pageNameId="hardwareListing.bannerTitle"
          pageRoute="/hardware/v1"
        />
      )}
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPageV2
          inputFilter={hardwareSearch ?? ''}
          urlFromMap={urlFromMap}
        />
      </div>
    </>
  );
};

export default HardwareV2;
