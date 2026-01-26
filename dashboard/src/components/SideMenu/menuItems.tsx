import type { JSX } from 'react';

import { MdOutlineMonitorHeart } from 'react-icons/md';
import { RxRadiobutton } from 'react-icons/rx';
import { ImTree } from 'react-icons/im';
import { HiOutlineDocumentSearch } from 'react-icons/hi';

import type { MessagesKey } from '@/locales/messages';
import { DOCUMENTATION_URL } from '@/utils/constants/general';
import type { PossibleMonitorPath } from '@/types/general';

export type RouteMenuItems = {
  navigateTo: PossibleMonitorPath;
  idIntl: MessagesKey;
  icon: JSX.Element;
  selected: boolean;
};

export type LinkMenuItems = {
  url: string;
  idIntl: MessagesKey;
  icon: JSX.Element;
};

export type LinkStringItems = {
  url: string;
  label: string;
};

const TreeIcon = <ImTree className="size-5" />;
const MonitorHeartIcon = <MdOutlineMonitorHeart className="size-5" />;
const RadioButtonIcon = <RxRadiobutton className="size-5" />;
const DocumentSearchIcon = <HiOutlineDocumentSearch />;

export const routeItems: RouteMenuItems[] = [
  {
    navigateTo: '/tree',
    idIntl: 'routes.treeMonitor',
    icon: TreeIcon,
    selected: true,
  },
  {
    navigateTo: '/hardware',
    idIntl: 'routes.hardwareMonitor',
    icon: MonitorHeartIcon,
    selected: false,
  },
  {
    navigateTo: '/issues',
    idIntl: 'routes.issueMonitor',
    icon: RadioButtonIcon,
    selected: false,
  },
];

export const linkItems: LinkMenuItems[] = [
  {
    url: DOCUMENTATION_URL,
    idIntl: 'global.documentation',
    icon: DocumentSearchIcon,
  },
];

export const dashboardItems: LinkStringItems[] = [
  {
    url: 'https://kdevops.org/',
    label: 'kdevops',
  },
  {
    url: 'https://netdev.bots.linux.dev/contest.html',
    label: 'netdev-CI',
  },
];
