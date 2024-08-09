import { ChangeEvent, useCallback, useState } from 'react';

import TreeListingPage from '@/components/TreeListingPage/TreeListingPage';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

const Trees = (): JSX.Element => {
  const [inputSearchText, setInputSearchText] = useState('');

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setInputSearchText(e.target.value);
    },
    [],
  );

  return (
    <>
      <div className="w-full bg-lightGray px-16 pt-24">
        <TreeListingPage inputFilter={inputSearchText} />
      </div>
      <div className="fixed top-0 mx-52 flex w-full pl-6 pr-12 pt-5">
        <div className="flex w-2/3 items-center px-6">
          {/* placeholder for search */}
          {/* TODO: use i18n for the input placeholder */}
          <DebounceInput
            onChange={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            placeholder="Search by tree, branch or tag"
            interval={DEBOUNCE_INTERVAL}
          />
        </div>
      </div>
    </>
  );
};

const DEBOUNCE_INTERVAL = 300;

export default Trees;
