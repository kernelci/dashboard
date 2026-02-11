import type { JSX } from 'react';
import { useSearch } from '@tanstack/react-router';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import TreeListingV2 from '@/components/TreeListingPage/TreeListingV2';
import { NewPageBanner } from '@/components/Banner/PageBanner';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';
import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

const TreeListingPageV2 = ({
  urlFromMap,
}: {
  urlFromMap: TreeListingRoutesMap['v2'];
}): JSX.Element => {
  const { treeListingVersion } = useFeatureFlag();
  const { treeSearch } = useSearch({
    from: urlFromMap.search,
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/tree" search={treeSearch} />
      {treeListingVersion !== 'v2' && (
        <NewPageBanner
          pageNameId="treeListing.treeListing"
          pageRoute="/tree/v1"
        />
      )}
      <div className="bg-light-gray w-full py-4">
        <TreeListingV2 inputFilter={treeSearch} urlFromMap={urlFromMap} />
      </div>
    </>
  );
};

export default TreeListingPageV2;
