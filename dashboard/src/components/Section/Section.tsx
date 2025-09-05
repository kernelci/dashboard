import type { ReactElement, ReactNode, ElementType, JSX } from 'react';
import { useMemo } from 'react';

import type { DialogTriggerProps } from '@radix-ui/react-dialog';

import type { ILinkWithIcon } from '@/components/LinkWithIcon/LinkWithIcon';
import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

import CopyButton from '@/components/Button/CopyButton';

import { LinkIcon } from '@/components/Icons/Link';

export interface ISection {
  title: string;
  subtitle?: string | ReactElement;
  rightIcon?: JSX.Element;
  leftIcon?: JSX.Element;
  subsections?: ISubsection[];
  eyebrow?: string | ReactElement;
}

export interface SubsectionLink extends ILinkWithIcon {
  wrapperComponent?: ElementType<{ children: ReactNode } & DialogTriggerProps>;
  copyValue?: string;
  children?: JSX.Element;
}

// TODO: move the children from inside the info to the subsection itself
export interface ISubsection {
  infos: SubsectionLink[];
  title?: string;
}

export const Subsection = ({ infos, title }: ISubsection): JSX.Element => {
  const [items, children] = useMemo(() => {
    const childrenList: JSX.Element[] = [];
    const itemList = infos
      .map(info => {
        const WrapperComponent = info.wrapperComponent;
        const shouldHaveLinkComponent =
          info.title !== undefined ||
          info.link !== undefined ||
          info.linkComponent !== undefined ||
          info.linkText !== undefined ||
          info.unformattedTitle !== undefined ||
          info.icon !== undefined ||
          info.onClick !== undefined;
        const LinkComponent = shouldHaveLinkComponent && (
          <LinkWithIcon
            key={info.title?.toString()}
            title={info.title}
            link={info.link}
            titleIcon={info.titleIcon}
            linkComponent={info.linkComponent}
            linkText={info.linkText}
            unformattedTitle={info.unformattedTitle}
            icon={
              info.link && !info.icon ? (
                <LinkIcon className="text-blue text-xl" />
              ) : (
                info.icon
              )
            }
            onClick={info.onClick ?? undefined}
          />
        );

        if (info.children !== undefined) {
          childrenList.push(info.children);
        } else {
          if (
            WrapperComponent !== undefined ||
            LinkComponent !== undefined ||
            info.copyValue !== undefined
          ) {
            return (
              <div key={info.title} className="flex flex-row items-end">
                {WrapperComponent ? (
                  <WrapperComponent asChild>{LinkComponent}</WrapperComponent>
                ) : (
                  <>{LinkComponent}</>
                )}
                {info.copyValue && <CopyButton value={info.copyValue} />}
              </div>
            );
          }
        }
      })
      .filter(item => item !== undefined);

    return [itemList, childrenList];
  }, [infos]);

  return (
    <div className="border-dark-gray border-t pt-4">
      {title && <span className="text-xl">{title}</span>}
      {items.length > 0 && (
        <div className="grid grid-cols-2 gap-x-8 gap-y-11 pb-4">{items}</div>
      )}
      {children.length > 0 && <div className="mb-4 w-[80vw]">{children}</div>}
    </div>
  );
};

const Section = ({
  title,
  subtitle,
  subsections,
  eyebrow,
  rightIcon,
  leftIcon,
}: ISection): JSX.Element => {
  const sections: JSX.Element[] | undefined = useMemo(
    () =>
      subsections?.map((subsection, index) => (
        <Subsection
          key={index}
          infos={subsection.infos}
          title={subsection.title}
        />
      )),
    [subsections],
  );

  return (
    <div className="text-dim-gray mb-6 flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        {eyebrow && <span className="text-sm">{eyebrow}</span>}
        <div className="flex flex-row items-center gap-2">
          {leftIcon}
          {title && (
            <span className="max-w-full text-2xl font-bold break-all">
              {title}
            </span>
          )}
          {rightIcon}
        </div>
        {subtitle}
      </div>
      {sections}
    </div>
  );
};

export default Section;
