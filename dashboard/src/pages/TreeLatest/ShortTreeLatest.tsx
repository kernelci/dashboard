import type { JSX } from 'react';

import { TreeLatest } from './TreeLatest';

export const ShortTreeLatest = (): JSX.Element => {
  return <TreeLatest urlFrom="/_main/(alternatives)/c/$treeName/$branch/" />;
};
