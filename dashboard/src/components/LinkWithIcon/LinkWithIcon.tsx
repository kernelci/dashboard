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
  className?: string;
  titleClassName?: string;
  truncate?: boolean;
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
  className,
  titleClassName,
  truncate = false,
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
    <div
      className={cn(
        'flex max-w-full min-w-0 flex-col items-start gap-1 text-[16px]',
        className,
      )}
    >
      {(titleText || titleIcon) && (
        <div className="flex flex-row items-center gap-[5px]">
          {titleText && (
            <span
              className={cn(
                'min-w-0 break-words',
                titleClassName ?? 'font-bold',
              )}
            >
              {titleText}
            </span>
          )}
          {titleIcon}
        </div>
      )}
      {linkComponent ?? (
        <WrapperLink
          className={cn(
            'flex max-w-full min-w-0 flex-row items-center gap-1',
            truncate ? 'overflow-hidden' : 'wrap-anywhere',
            {
              'underline hover:text-gray-900': onClick || link,
            },
          )}
          href={link}
          title={link}
          target="_blank"
          rel="noreferrer"
          onClick={onClick}
        >
          {truncate ? (
            <span className="min-w-0 truncate">{linkText}</span>
          ) : (
            linkText
          )}
          {icon && <span className={cn(truncate && 'shrink-0')}>{icon}</span>}
        </WrapperLink>
      )}
    </div>
  );
};

export default LinkWithIcon;