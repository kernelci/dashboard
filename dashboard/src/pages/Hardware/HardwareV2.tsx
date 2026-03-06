import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import HardwareListingPageV2 from '@/pages/Hardware/HardwareListingPageV2';

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

  return (
    <>
      <MemoizedListingOGTags monitor="/hardware" search={hardwareSearch} />
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
