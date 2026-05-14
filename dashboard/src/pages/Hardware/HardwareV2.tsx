import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import HardwareListingPageV2 from '@/pages/Hardware/HardwareListingPageV2';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import { NewPageBanner } from '@/components/Banner/PageBanner';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';
import { parseSearchIntent } from '@/lib/intent';

export const HardwareV2 = ({
  urlFromMap,
}: {
  urlFromMap: HardwareListingRoutesMap['v2'];
}): JSX.Element => {
  const { hardwareListingVersion } = useFeatureFlag();
  const { hardwareSearch } = useSearch({
    from: urlFromMap.search,
  });

  const intent = parseSearchIntent(hardwareSearch ?? '');

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
        <HardwareListingPageV2 intent={intent} urlFromMap={urlFromMap} />
      </div>
    </>
  );
};

export default HardwareV2;
