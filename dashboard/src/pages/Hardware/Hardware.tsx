import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import HardwareListingPage from '@/pages/Hardware/HardwareListingPage';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';
import { parseSearchIntent } from '@/lib/intent';

const Hardware = ({
  urlFromMap,
}: {
  urlFromMap: HardwareListingRoutesMap;
}): JSX.Element => {
  const { hardwareSearch } = useSearch({
    from: urlFromMap.search,
  });

  const intent = parseSearchIntent(hardwareSearch ?? '');

  return (
    <>
      <MemoizedListingOGTags monitor="/hardware" search={hardwareSearch} />
      <div className="bg-light-gray w-full py-10">
        <HardwareListingPage intent={intent} urlFromMap={urlFromMap} />
      </div>
    </>
  );
};

export default Hardware;
