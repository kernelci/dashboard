import type { ReactElement } from 'react';

import { FormattedMessage } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';

export interface ILinkWithIcon {
  title?: MessagesKey;
  linkText?: string | ReactElement;
  link?: string;
  icon?: ReactElement;
  linkComponent?: ReactElement;
  onClick?: () => void;
}

const LinkWithIcon = ({
  title,
  linkText,
  icon,
  link,
  linkComponent,
  onClick,
}: ILinkWithIcon): JSX.Element => {
  const WrapperLink = link ? 'a' : 'div';
  return (
    <div className="flex flex-col items-start gap-2 text-sm">
      {title && (
        <span className="font-bold">
          <FormattedMessage id={title} />
        </span>
      )}
      {linkComponent ?? (
        <WrapperLink
          className="flex flex-row items-center gap-1"
          href={link}
          target="_blank"
          rel="noreferrer"
          onClick={onClick}
        >
          {linkText}
          {icon}
        </WrapperLink>
      )}
    </div>
  );
};

export default LinkWithIcon;
