import type { JSX, ReactNode } from 'react';

import { FormattedMessage } from 'react-intl';

import { MdDeveloperBoard } from 'react-icons/md';

import { valueOrEmpty } from '@/lib/string';
import type { MessagesKey } from '@/locales/messages';
import type { HardwareRegistryInfo } from '@/lib/hardwareRegistryMock';

import BaseCard from '@/components/Cards/BaseCard';
import { DetailsInfoCard } from '@/components/Cards/DetailsInfoCard';
import LinkWithIcon, {
  type ILinkWithIcon,
} from '@/components/LinkWithIcon/LinkWithIcon';
import { LinkIcon } from '@/components/Icons/Link';

const humanize = (text?: string): string | undefined =>
  text?.replace(/_/g, ' ');

const processorFields = (info: HardwareRegistryInfo): ILinkWithIcon[] => {
  const clock = info.processor?.maxClockSpeedMhz;
  return [
    {
      title: 'global.soc',
      linkText: valueOrEmpty(info.processor?.id),
      link: info.processor?.url,
    },
    {
      title: 'global.architecture',
      linkText: valueOrEmpty(info.processor?.architecture),
    },
    {
      title: 'global.cores',
      linkText: valueOrEmpty(info.processor?.cores?.toString()),
    },
    {
      title: 'global.maxClockSpeed',
      linkText: valueOrEmpty(clock ? `${clock} MHz` : undefined),
    },
    {
      title: 'global.siliconVendor',
      linkText: valueOrEmpty(info.siliconVendor?.id),
      link: info.siliconVendor?.url,
    },
  ];
};

const boardFields = (info: HardwareRegistryInfo): ILinkWithIcon[] => [
  {
    title: 'global.boardType',
    linkText: valueOrEmpty(humanize(info.boardType)),
  },
  {
    title: 'global.formFactor',
    linkText: valueOrEmpty(humanize(info.formFactor)),
  },
  ...(info.systemModule
    ? [
        {
          title: 'global.systemModule' as MessagesKey,
          linkText: valueOrEmpty(info.systemModule.id),
          link: info.systemModule.url,
        },
      ]
    : []),
  {
    title: 'global.vendor',
    linkText: valueOrEmpty(info.vendor?.id),
    link: info.vendor?.url,
  },
];

const fieldByTitle = (
  fields: ILinkWithIcon[],
  title: MessagesKey,
): ILinkWithIcon | undefined => fields.find(field => field.title === title);

const listingFields = (info: HardwareRegistryInfo): ILinkWithIcon[] => {
  const processor = processorFields(info);
  const board = boardFields(info);
  return [
    {
      title: 'global.platform',
      linkText: valueOrEmpty(info.platformId),
      link: info.url,
    },
    fieldByTitle(processor, 'global.soc'),
    fieldByTitle(processor, 'global.architecture'),
    fieldByTitle(board, 'global.vendor'),
    fieldByTitle(board, 'global.boardType'),
    fieldByTitle(board, 'global.formFactor'),
  ].filter((field): field is ILinkWithIcon => field !== undefined);
};

const SpecGroup = ({
  label,
  children,
}: {
  label: MessagesKey;
  children: ReactNode;
}): JSX.Element => (
  <div className="flex flex-col gap-2">
    <span className="text-dark-gray2 text-xs font-medium tracking-wide uppercase">
      <FormattedMessage id={label} />
    </span>
    <div className="flex flex-wrap items-start gap-x-8 gap-y-3">{children}</div>
  </div>
);

const specs = (fields: ILinkWithIcon[]): JSX.Element[] =>
  fields.map(field => (
    <LinkWithIcon
      key={field.title}
      titleClassName="text-dark-gray2 text-xs font-normal"
      {...field}
    />
  ));

const RegistryTitle = ({
  info,
}: {
  info: HardwareRegistryInfo;
}): JSX.Element => (
  <div className="flex flex-col gap-1">
    <div className="flex flex-wrap items-center gap-2">
      <MdDeveloperBoard className="text-blue text-xl" />
      <LinkWithIcon linkText={info.platformId} link={info.url} />
    </div>
    {info.description && (
      <span className="text-dark-gray2 text-sm font-normal">
        {info.description}
      </span>
    )}
  </div>
);

export const HardwareRegistryListingDetails = ({
  info,
}: {
  info: HardwareRegistryInfo;
}): JSX.Element => (
  <div className="bg-light-gray flex flex-col gap-3 py-4 pr-4 pl-12">
    {info.description && (
      <span className="text-dark-gray2 text-sm">{info.description}</span>
    )}
    <div className="flex flex-wrap items-start gap-x-8 gap-y-3">
      {specs(listingFields(info))}
    </div>
  </div>
);

export const HardwareRegistryStrip = ({
  info,
  className,
}: {
  info?: HardwareRegistryInfo;
  className?: string;
}): JSX.Element | null => {
  if (!info) {
    return null;
  }

  return (
    <BaseCard className={className} title={<RegistryTitle info={info} />}>
      <div className="flex flex-col gap-4 px-3 pb-4">
        <SpecGroup label="global.processor">
          {specs(processorFields(info))}
        </SpecGroup>
        <div className="border-dark-gray border-t" />
        <SpecGroup label="global.board">{specs(boardFields(info))}</SpecGroup>
      </div>
    </BaseCard>
  );
};

export const HardwareRegistryCard = ({
  info,
}: {
  info?: HardwareRegistryInfo;
}): JSX.Element | null => {
  if (!info) {
    return null;
  }

  return (
    <DetailsInfoCard
      title={
        <div className="flex items-center gap-2">
          <MdDeveloperBoard className="text-blue text-xl" />
          <FormattedMessage id="testDetails.hardwareInfo" />
        </div>
      }
      data={[
        {
          title: 'global.platform' as MessagesKey,
          linkText: valueOrEmpty(info.platformId),
          link: info.url,
        },
        {
          title: 'global.description' as MessagesKey,
          linkText: valueOrEmpty(info.description),
        },
        ...processorFields(info),
        ...boardFields(info),
      ].map(field =>
        field.link
          ? { ...field, icon: <LinkIcon className="text-blue text-xl" /> }
          : field,
      )}
    />
  );
};
