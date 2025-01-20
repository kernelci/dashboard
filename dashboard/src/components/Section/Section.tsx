import { FiLink } from 'react-icons/fi';

import type { ReactElement, ReactNode, ElementType } from 'react';
import { useMemo } from 'react';

import type { DialogTriggerProps } from '@radix-ui/react-dialog';

import type { ILinkWithIcon } from '@/components/LinkWithIcon/LinkWithIcon';
import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

import CopyButton from '@/components/Button/CopyButton';

export interface ISection {
  title: string;
  subsections?: ISubsection[];
  eyebrow?: string | ReactElement;
}

export interface SubsectionLink extends ILinkWithIcon {
  wrapperComponent?: ElementType<{ children: ReactNode } & DialogTriggerProps>;
  copyValue?: string;
}
export interface ISubsection {
  infos: SubsectionLink[];
}

export const Subsection = ({ infos }: ISubsection): JSX.Element => {
  const items = useMemo(
    () =>
      infos.map(info => {
        const WrapperComponent = info.wrapperComponent;
        const LinkComponent = (
          <LinkWithIcon
            key={info.title?.toString()}
            title={info.title}
            link={info.link}
            linkComponent={info.linkComponent}
            linkText={info.linkText}
            unformattedTitle={info.unformattedTitle}
            icon={
              info.link && !info.icon ? (
                <FiLink className="text-blue" />
              ) : (
                info.icon
              )
            }
            onClick={info.onClick ?? undefined}
          />
        );
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
      }),
    [infos],
  );
  return (
    <div className="grid grid-cols-2 gap-8 border-t border-darkGray py-8">
      {items}
    </div>
  );
};

const Section = ({ title, subsections, eyebrow }: ISection): JSX.Element => {
  const sections = useMemo(
    () =>
      subsections?.map((subsection, index) => (
        <Subsection key={index} infos={subsection.infos} />
      )),
    [subsections],
  );
  return (
    <div className="flex flex-col gap-4 text-dimGray">
      <div className="flex flex-col gap-2">
        <span className="text-sm">{eyebrow}</span>
        <span className="text-2xl font-bold">{title}</span>
      </div>
      {sections}
    </div>
  );
};

export default Section;
