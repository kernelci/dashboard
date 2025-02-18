import { useMemo, type JSX } from 'react';

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
          subtitle={section.subtitle}
          subsections={section.subsections}
          eyebrow={section.eyebrow}
          leftIcon={section.leftIcon}
          rightIcon={section.rightIcon}
        />
      )),
    [sections],
  );
  return <div className="flex flex-col gap-8">{groupSections}</div>;
};

export default SectionGroup;
