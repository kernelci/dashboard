import type { ReactElement, ReactNode, ElementType, JSX } from 'react';
import { useMemo } from 'react';

import type { DialogTriggerProps } from '@radix-ui/react-dialog';

import type { ILinkWithIcon } from '@/components/LinkWithIcon/LinkWithIcon';
import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

import CopyButton from '@/components/Button/CopyButton';
import BaseCard from '@/components/Cards/BaseCard';

import { LinkIcon } from '@/components/Icons/Link';
import { isHttpUrl } from '@/lib/string';

import { cn } from '@/lib/utils';
import { isUrl } from '@/lib/string';

const SPAN_CLASS = {
  1: 'col-span-1',
  2: 'col-span-2',
  3: 'col-span-3',
  4: 'col-span-4',
} as const;

export type FieldSpan = keyof typeof SPAN_CLASS;

export interface ISection {
  title: string;
  subtitle?: string | ReactElement;
  rightIcon?: JSX.Element;
  leftIcon?: JSX.Element;
  actions?: JSX.Element;
  subsections?: ISubsection[];
  eyebrow?: string | ReactElement;
  card?: boolean;
}

export interface SubsectionLink extends ILinkWithIcon {
  wrapperComponent?: ElementType<{ children: ReactNode } & DialogTriggerProps>;
  copyValue?: string;
  children?: JSX.Element;
  span?: FieldSpan;
}

// TODO: move the children from inside the info to the subsection itself
export interface ISubsection {
  infos: SubsectionLink[];
  title?: string;
}

export const Subsection = ({
  infos,
  title,
  card = false,
}: ISubsection & { card?: boolean }): JSX.Element => {
  const [items, children] = useMemo(() => {
    const childrenList: JSX.Element[] = [];
    const itemList = infos
      .map(info => {
        const WrapperComponent = info.wrapperComponent;
        const url = info.link && isUrl(info.link) ? info.link : undefined;
        const span = info.span ?? 1;
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
            linkText={url ?? info.linkText}
            unformattedTitle={info.unformattedTitle}
            icon={
              info.link && isHttpUrl(info.link) && !info.icon ? (
                <LinkIcon className="text-blue text-xl" />
              ) : (
                info.icon
              )
            }
            onClick={info.onClick ?? undefined}
            titleClassName="text-dark-gray2 text-xs font-normal"
            className={card ? 'w-full text-sm' : undefined}
            truncate={url !== undefined}
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
              <div
                key={info.title}
                className={cn(
                  'flex max-w-full min-w-0 flex-row items-start',
                  SPAN_CLASS[span],
                )}
              >
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
  }, [card, infos]);

  return (
    <div className="border-dark-gray flex flex-col gap-2 border-t pt-3">
      {title && (
        <span className="text-dark-gray2 max-w-full text-xs font-medium tracking-wide break-all uppercase">
          {title}
        </span>
      )}
      {items.length > 0 && (
        <div className="grid grid-cols-4 items-start gap-x-6 gap-y-3">
          {items}
        </div>
      )}
      {children.length > 0 && <div>{children}</div>}
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
  actions,
  card = false,
}: ISection): JSX.Element => {
  const sections: JSX.Element[] | undefined = useMemo(
    () =>
      subsections?.map((subsection, index) => (
        <Subsection
          key={index}
          card={card}
          infos={subsection.infos}
          title={subsection.title}
        />
      )),
    [card, subsections],
  );

  const header = (
    <div className="flex flex-col gap-1 pr-3 font-normal">
      {eyebrow && <span className="text-sm">{eyebrow}</span>}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <span className="inline-flex w-fit max-w-full shrink-0 items-start gap-2">
          {leftIcon && (
            <span className="mt-0.5 shrink-0 [&_svg]:h-6 [&_svg]:w-6">
              {leftIcon}
            </span>
          )}
          {title && (
            <span className="min-w-0 text-xl font-bold break-words">
              {title}
            </span>
          )}
        </span>
        {rightIcon && <span className="max-w-full shrink-0">{rightIcon}</span>}
        {actions && <span className="ml-auto shrink-0">{actions}</span>}
      </div>
      {subtitle}
    </div>
  );

  if (card) {
    return (
      <BaseCard
        className="mb-0"
        title={
          <span className="flex items-center gap-2">
            {leftIcon}
            <span className="min-w-0">{title}</span>
            {rightIcon}
          </span>
        }
      >
        <div className="flex flex-col gap-4 px-3 pb-4 [&>div:first-child]:border-t-0 [&>div:first-child]:pt-0">
          {subtitle}
          {sections}
        </div>
      </BaseCard>
    );
  }

  return (
    <div className="text-dim-gray flex flex-col gap-2">
      {header}
      {sections}
    </div>
  );
};

export default Section;
