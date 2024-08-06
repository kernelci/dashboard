import { ReactElement, useMemo } from 'react';

import LinkWithIcon from '../LinkWithIcon/LinkWithIcon';

interface ILinkGroup {
  links: (ILink | undefined)[];
}

interface ILink {
  linkText: JSX.Element;
  title?: ReactElement;
  link?: string;
  icon?: ReactElement;
}

const LinksGroup = ({ links }: ILinkGroup): JSX.Element => {
  const linkGroup = useMemo(() => {
    return links?.map(
      link =>
        link && (
          <LinkWithIcon
            title={link.title}
            icon={link.icon}
            linkText={link.linkText}
            key={link.link}
            link={link.link}
          />
        ),
    );
  }, [links]);
  return (
    <div className="grid min-w-[350px] grid-cols-3 gap-4">{linkGroup}</div>
  );
};

export default LinksGroup;
