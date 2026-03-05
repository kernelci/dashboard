import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import HardwareListingPage from '@/pages/Hardware/HardwareListingPage';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import { OldPageBanner } from '@/components/Banner/PageBanner';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

const Hardware = ({
  urlFromMap,
}: {
  urlFromMap: HardwareListingRoutesMap['v1'];
}): JSX.Element => {
  const { hardwareListingVersion } = useFeatureFlag();
  const { hardwareSearch } = useSearch({
    from: urlFromMap.search,
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/hardware" search={hardwareSearch} />
      {hardwareListingVersion !== 'v1' && (
        <OldPageBanner
          pageNameId="hardwareListing.bannerTitle"
          pageRoute="/hardware"
        />
      )}
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPage
          inputFilter={hardwareSearch ?? ''}
          urlFromMap={urlFromMap}
        />
      </div>
    </>
  );
};

export default Hardware;
