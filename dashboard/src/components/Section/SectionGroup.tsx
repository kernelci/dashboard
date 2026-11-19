import type { JSX } from 'react';

import type { ISection } from './Section';
import Section from './Section';

interface ISectionGroup {
  sections: ISection[];
}

const SectionGroup = ({ sections }: ISectionGroup): JSX.Element => (
  <div className="flex flex-col gap-6">
    {sections.map(section => (
      <Section key={section.title} {...section} />
    ))}
  </div>
);

export default SectionGroup;
