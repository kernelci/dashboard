import { type ReactElement, type JSX, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';
import { isHttpUrl } from '@/lib/string';
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
}: ILinkWithIcon): JSX.Element => {
  const href = link && isHttpUrl(link) ? link : undefined;
  const rowClassName = cn('flex flex-row items-center gap-1', {
    'underline hover:text-gray-900': onClick || href,
  });

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
      className={cn('flex flex-col items-start gap-1 text-[16px]', className)}
    >
      {(titleText || titleIcon) && (
        <div className="flex flex-row gap-[5px]">
          {titleText && <span className="font-bold">{titleText}</span>}
          {titleIcon}
        </div>
      )}
      {linkComponent ??
        (href ? (
          <a
            className={rowClassName}
            href={href}
            target="_blank"
            rel="noreferrer"
            onClick={onClick}
          >
            {linkText}
            {icon}
          </a>
        ) : (
          <span className={rowClassName} onClick={onClick}>
            {linkText}
            {icon}
          </span>
        ))}
    </div>
  );
};

export default LinkWithIcon;
