import { useMemo } from 'react';

import Section, { ISection } from './Section';

interface ISectionGroup {
  sections: ISection[];
}

const SectionGroup = ({ sections }: ISectionGroup): JSX.Element => {
  const groupSections = useMemo(
    () =>
      sections.map(section => (
        <Section
          key={section.title}
          title={section.title}
          subsections={section.subsections}
          eyebrow={section.eyebrow}
        />
      )),
    [sections],
  );
  return <div className="flex flex-col gap-8">{groupSections}</div>;
};

export default SectionGroup;
