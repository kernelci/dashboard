import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import TreeListingPage from '@/components/TreeListingPage/TreeListingPage';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import { OldPageBanner } from '@/components/Banner/PageBanner';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';
import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

const Trees = ({
  urlFromMap,
}: {
  urlFromMap: TreeListingRoutesMap['v1'];
}): JSX.Element => {
  const { treeListingVersion } = useFeatureFlag();
  const { treeSearch } = useSearch({
    from: urlFromMap.search,
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/tree" search={treeSearch} />
      {treeListingVersion !== 'v1' && (
        <OldPageBanner pageNameId="treeListing.treeListing" pageRoute="/tree" />
      )}
      <div className="bg-light-gray w-full py-4">
        <TreeListingPage inputFilter={treeSearch} urlFromMap={urlFromMap} />
      </div>
    </>
  );
};

export default Trees;
