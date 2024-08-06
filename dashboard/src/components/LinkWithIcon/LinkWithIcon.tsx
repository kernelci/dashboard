import { ReactElement } from 'react';

export interface ILinkWithIcon {
  title?: string | ReactElement;
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
  return (
    <div className="flex flex-col gap-2 text-sm">
      <span className="font-bold">{title}</span>
      <a
        className="flex flex-row items-center gap-1"
        href={link}
        target="_blank"
        rel="noreferrer"
      >
        {linkText}
        {icon}
      </a>
    </div>
  );
};

export default LinkWithIcon;
