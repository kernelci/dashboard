import { ReactElement } from 'react';

import { FormattedMessage } from 'react-intl';

import { MessagesKey } from '@/locales/messages';

export interface ILinkWithIcon {
  title?: MessagesKey;
  linkText?: string | ReactElement;
  link?: string;
  icon?: ReactElement;
}

const LinkWithIcon = ({
  title,
  linkText,
  icon,
  link,
}: ILinkWithIcon): JSX.Element => {
  const WrapperLink = link ? 'a' : 'div';
  return (
    <div className="flex flex-col items-start gap-2 text-sm">
      <span className="font-bold">
        <FormattedMessage id={title} />
      </span>
      <WrapperLink
        className="flex flex-row items-center gap-1"
        href={link}
        target="_blank"
        rel="noreferrer"
      >
        {linkText}
        {icon}
      </WrapperLink>
    </div>
  );
};

export default LinkWithIcon;
