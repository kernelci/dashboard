import { ChangeEvent, useCallback, useState } from 'react';

import TreeListingPage from '@/components/TreeListingPage/TreeListingPage';

import { Input } from '@/components/ui/input';

import { useDebounce } from '../../hooks/useDebounce';

const Trees = (): JSX.Element => {
  const [inputSearchText, setInputSearchText] = useState('');
  const debouncedInput = useDebounce(inputSearchText, DEBOUNCE_INTERVAL);

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setInputSearchText(e.target.value);
    },
    [],
  );

  return (
    <>
      <div className="w-full px-16 pt-24 bg-lightGray">
        <TreeListingPage inputFilter={debouncedInput} />
      </div>
      <div className="flex fixed top-0 mx-52 pl-6 pr-12 pt-5 w-full">
        <div className="flex w-2/3 px-6 items-center">
          {/* placeholder for search */}
          {/* TODO: use i18n for the input placeholder */}
          <Input
            onChange={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            placeholder="Search by tree, branch or tag"
          />
        </div>
      </div>
    </>
  );
};

const DEBOUNCE_INTERVAL = 300;

export default Trees;
