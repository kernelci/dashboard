import type { ChangeEvent, JSX } from 'react';
import { useCallback } from 'react';

import { useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
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

  const navigate = useNavigate({ from: urlFromMap.navigate });

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          treeSearch: e.target.value,
        }),
      });
    },
    [navigate],
  );

  const { formatMessage } = useIntl();

  return (
    <>
      <MemoizedListingOGTags monitor="/tree" search={treeSearch} />
      <div className="fixed top-0 z-10 mx-[380px] flex w-full pt-5 pr-12 pl-6">
        <div className="flex w-2/3 items-center px-6">
          <DebounceInput
            debouncedSideEffect={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            startingValue={treeSearch}
            placeholder={formatMessage({ id: 'tree.searchPlaceholder' })}
          />
        </div>
      </div>
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
