import { type ReactElement, type JSX, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';
import { cn } from '@/lib/utils';

export interface ILinkWithIcon {
  title?: MessagesKey;
  linkText?: string | ReactElement;
  link?: string;
  icon?: ReactElement;
  linkComponent?: ReactElement;
  onClick?: () => void;
  unformattedTitle?: string;
  titleIcon?: JSX.Element;
}

const LinkWithIcon = ({
  title,
  linkText,
  icon,
  link,
  linkComponent,
  onClick,
  unformattedTitle,
  titleIcon,
}: ILinkWithIcon): JSX.Element => {
  const WrapperLink = link ? 'a' : 'div';

  const titleText = useMemo(() => {
    if (title) {
      return <FormattedMessage id={title} />;
    } else if (unformattedTitle) {
      return unformattedTitle;
    }
    return null;
  }, [title, unformattedTitle]);

  return (
    <div className="flex flex-col items-start gap-1 text-[16px]">
      {(titleText || titleIcon) && (
        <div className="flex flex-row gap-[5px]">
          {titleText && <span className="font-bold">{titleText}</span>}
          {titleIcon}
        </div>
      )}
      {linkComponent ?? (
        <WrapperLink
          className={cn('flex flex-row items-center gap-1', {
            'underline hover:text-gray-900': onClick || link,
          })}
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
