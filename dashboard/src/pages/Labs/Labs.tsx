import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import type { LabsListingRoutesMap } from '@/utils/constants/labsListing';

import { LabsPage } from './LabsPage';

const Labs = ({
  urlFromMap,
}: {
  urlFromMap: LabsListingRoutesMap;
}): JSX.Element => {
  const { labsSearch } = useSearch({
    from: urlFromMap.search,
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/labs" search={labsSearch} />
      <div className="bg-light-gray w-full py-4">
        <LabsPage inputFilter={labsSearch} urlFromMap={urlFromMap} />
      </div>
    </>
  );
};

export default Labs;
