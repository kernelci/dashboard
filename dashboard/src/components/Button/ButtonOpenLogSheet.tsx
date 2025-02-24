import type { JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import { SheetTrigger } from '@/components/Sheet';
import { SearchIcon } from '@/components/Icons/SearchIcon';

const ButtonOpenLogSheet = ({
  setSheetToLog,
}: {
  setSheetToLog: () => void;
}): JSX.Element => (
  <SheetTrigger
    className="text-blue flex flex-row items-center gap-2 self-start"
    onClick={setSheetToLog}
  >
    <FormattedMessage id="global.viewLog" />
    <SearchIcon />
  </SheetTrigger>
);

export default ButtonOpenLogSheet;
