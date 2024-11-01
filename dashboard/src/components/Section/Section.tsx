import { FiLink } from 'react-icons/fi';

import type { ReactElement, ReactNode, ElementType } from 'react';
import { useMemo, Fragment } from 'react';

import type { ILinkWithIcon } from '@/components/LinkWithIcon/LinkWithIcon';
import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';

export interface ISection {
  title: string;
  subsections?: ISubsection[];
  eyebrow?: string | ReactElement;
}

interface SubsectionLink extends ILinkWithIcon {
  wrapperComponent?: ElementType<{ children: ReactNode }>;
}
export interface ISubsection {
  infos: SubsectionLink[];
}

export const Subsection = ({ infos }: ISubsection): JSX.Element => {
  const items = useMemo(
    () =>
      infos.map(info => {
        const WrapperComponent = info.wrapperComponent ?? Fragment;
        return (
          <WrapperComponent key={info.title}>
            <LinkWithIcon
              key={info.title?.toString()}
              title={info.title}
              link={info.link}
              linkText={info.linkText}
              icon={
                info.link && !info.icon ? (
                  <FiLink className="text-blue" />
                ) : (
                  info.icon
                )
              }
            />
          </WrapperComponent>
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
      subsections?.map(subsection => (
        <Subsection key={subsection.infos[0].link} infos={subsection.infos} />
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
