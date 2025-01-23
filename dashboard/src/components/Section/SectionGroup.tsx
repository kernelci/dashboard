import { useMemo } from 'react';

import type { ISection } from './Section';
import Section from './Section';

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
          icon={section.icon}
        />
      )),
    [sections],
  );
  return <div className="flex flex-col gap-8">{groupSections}</div>;
};

export default SectionGroup;
