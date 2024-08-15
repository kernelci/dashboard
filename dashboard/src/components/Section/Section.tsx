import { ReactElement, useMemo } from 'react';

import LinkWithIcon, { ILinkWithIcon } from '../LinkWithIcon/LinkWithIcon';

export interface ISection {
  title: string;
  subsections?: ISubsection[];
  eyebrow?: string | ReactElement;
}

export interface ISubsection {
  infos: ILinkWithIcon[];
}

export const Subsection = ({ infos }: ISubsection): JSX.Element => {
  const items = useMemo(
    () =>
      infos.map(info => (
        <LinkWithIcon
          key={info.title?.toString()}
          title={info.title}
          link={info.link}
          linkText={info.linkText}
          icon={info.icon}
        />
      )),
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
