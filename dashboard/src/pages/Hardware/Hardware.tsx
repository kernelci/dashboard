import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import HardwareListingPage from '@/pages/Hardware/HardwareListingPage';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import { OldPageBanner } from '@/components/Banner/PageBanner';

const Hardware = (): JSX.Element => {
  const { hardwareSearch } = useSearch({
    from: '/_main/hardware/v1',
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/hardware" search={hardwareSearch} />
      <OldPageBanner
        pageNameId="hardwareListing.bannerTitle"
        pageRoute="/hardware"
      />
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPage inputFilter={hardwareSearch ?? ''} />
      </div>
    </>
  );
};

export default Hardware;
