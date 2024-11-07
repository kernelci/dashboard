import { FormattedMessage } from 'react-intl';

import { useSearch, useNavigate, useLocation } from '@tanstack/react-router';
import { useCallback, useEffect, useMemo } from 'react';

import Select, { SelectItem } from '@/components/Select/Select';
import type { TOrigins } from '@/types/tree/Tree';
import { zOrigin, zOriginEnum } from '@/types/tree/Tree';

const OriginSelect = (): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const navigate = useNavigate({ from: '/' });

  const onValueChange = useCallback(
    (value: TOrigins) => {
      navigate({
        to: '/',
        search: previousSearch => ({ ...previousSearch, origin: value }),
      });
    },
    [navigate],
  );

  const selectItems = useMemo(
    () =>
      zOriginEnum.options.map(option => (
        <SelectItem key={option} value={option}>
          {option}
        </SelectItem>
      )),
    [],
  );

  useEffect(() => {
    if (unsafeOrigin === undefined)
      navigate({
        search: previousSearch => ({ ...previousSearch, origin: origin }),
      });
  });

  return (
    <div className="flex items-center">
      <span className="mr-4 text-base font-medium text-dimGray">
        <FormattedMessage id="global.origin" />
      </span>
      <Select onValueChange={onValueChange} value={origin}>
        {selectItems}
      </Select>
    </div>
  );
};

const TitleName = ({ basePath }: { basePath: string }): JSX.Element => {
  switch (basePath) {
    case 'tree':
      return <FormattedMessage id="routes.treeMonitor" />;
    case 'hardware':
      return <FormattedMessage id="routes.hardwareMonitor" />;
    default:
      return <FormattedMessage id="routes.unknown" />;
  }
};

const TopBar = (): JSX.Element => {
  const { pathname } = useLocation();

  const basePath = pathname.split('/')[1] ?? '';

  return (
    <div className="fixed top-0 z-10 mx-52 flex h-20 w-full bg-white px-16">
      <div className="flex flex-row items-center justify-between">
        <span className="mr-14 text-2xl">
          <TitleName basePath={basePath} />
        </span>
        {basePath === 'tree' && <OriginSelect />}
      </div>
    </div>
  );
};

export default TopBar;
