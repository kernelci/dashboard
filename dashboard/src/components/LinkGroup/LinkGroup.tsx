import type { ElementType, ReactElement, ReactNode } from 'react';
import { Fragment, memo } from 'react';

import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';
import type { MessagesKey } from '@/locales/messages';

export interface ILinkGroup {
  links: (ILink | undefined)[];
}

interface ILink {
  linkText: JSX.Element;
  title: MessagesKey;
  link?: string;
  icon?: ReactElement;
  wrapperComponent?: ElementType<{ children: ReactNode }>;
}

type LinkGroupContainerProps = {
  children: ReactNode;
};

export const LinkGroupFilling = ({ links }: ILinkGroup): JSX.Element => {
  return (
    <>
      {links?.map(link => {
        if (link) {
          const WrapperComponent = link.wrapperComponent ?? Fragment;
          return (
            <WrapperComponent key={link.title}>
              <LinkWithIcon
                title={link.title}
                icon={link.icon}
                linkText={link.linkText}
                link={link.link}
              />
            </WrapperComponent>
          );
        }
      })}
    </>
  );
};

const MemoizedLinkGroupFilling = memo(LinkGroupFilling);

export const LinkGroupContainer = ({
  children,
}: LinkGroupContainerProps): JSX.Element => {
  return <div className="grid min-w-[350px] grid-cols-3 gap-4">{children}</div>;
};
const LinksGroup = ({ links }: ILinkGroup): JSX.Element => {
  return (
    <LinkGroupContainer>
      <MemoizedLinkGroupFilling links={links} />
    </LinkGroupContainer>
  );
};

export default LinksGroup;
