import { ChangeEvent, useCallback, useState } from 'react';

import SideMenu from '../SideMenu/SideMenu';
import TopBar from '../TopBar/TopBar';
import TreeListingPage from '../TreeListingPage/TreeListingPage';
import { useDebounce } from '../../hooks/useDebounce';

const Dashboard = (): JSX.Element => {
  const [inputSearchText, setInputSearchText] = useState('');
  const debouncedInput = useDebounce(inputSearchText, DEBOUNCE_INTERVAL);

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setInputSearchText(e.target.value);
    },
    [],
  );

  return (
    <div className="w-full h-full">
      <div className="flex flex-row w-full justify-between">
        <SideMenu />
        <TopBar onChangeInputText={onInputSearchTextChange} />
        <div className="w-full px-16 pt-24 bg-lightGray">
          <TreeListingPage inputFilter={debouncedInput} />
        </div>
      </div>
    </div>
  );
};

const DEBOUNCE_INTERVAL = 300;

export default Dashboard;
