import type { JSX } from 'react';

import { useSearch } from '@tanstack/react-router';

import TreeListingPage from '@/components/TreeListingPage/TreeListingPage';

import { MemoizedListingOGTags } from '@/components/OpenGraphTags/ListingOGTags';
import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

const Trees = ({
  urlFromMap,
}: {
  urlFromMap: TreeListingRoutesMap;
}): JSX.Element => {
  const { treeSearch } = useSearch({
    from: urlFromMap.search,
  });

  return (
    <>
      <MemoizedListingOGTags monitor="/tree" search={treeSearch} />
      <div className="bg-light-gray w-full py-4">
        <TreeListingPage inputFilter={treeSearch} urlFromMap={urlFromMap} />
      </div>
    </>
  );
};

export default Trees;
