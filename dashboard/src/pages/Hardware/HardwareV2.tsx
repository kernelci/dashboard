import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import HardwareListingPageV2 from '@/pages/Hardware/HardwareListingPageV2';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import { NewPageBanner } from '@/components/Banner/PageBanner';

export const HardwareV2 = (): JSX.Element => {
  const { hardwareSearch } = useSearch({
    from: '/_main/hardware',
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/hardware" search={hardwareSearch} />
      <NewPageBanner
        pageNameId="hardwareListing.bannerTitle"
        pageRoute="/hardware/v1"
      />
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPageV2 inputFilter={hardwareSearch ?? ''} />
      </div>
    </>
  );
};

export default HardwareV2;
