import { ChangeEvent, useCallback, useState } from 'react';

import { useIntl } from 'react-intl';

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

  const intl = useIntl();

  return (
    <>
      <div className="w-full bg-lightGray py-10">
        <TreeListingPage inputFilter={inputSearchText} />
      </div>
      <div className="fixed top-0 z-10 mx-[380px] flex w-full pl-6 pr-12 pt-5">
        <div className="flex w-2/3 items-center px-6">
          <DebounceInput
            onChange={onInputSearchTextChange}
            className="w-2/3"
            type="text"
            placeholder={intl.formatMessage({ id: 'global.placeholderSearch' })}
            interval={DEBOUNCE_INTERVAL}
          />
        </div>
      </div>
    </>
  );
};

const DEBOUNCE_INTERVAL = 300;

export default Trees;
