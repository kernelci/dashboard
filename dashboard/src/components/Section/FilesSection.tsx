import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import type { ISection, ISubsection, SubsectionLink } from './Section';

export const getFilesSection = ({
  inputFiles,
  outputFiles,
  title,
}: {
  inputFiles?: object;
  outputFiles?: object;
  title: string;
}): ISection | undefined => {
  if (!inputFiles && !outputFiles) {
    return;
  }

  const filesSubsections: ISubsection[] = [];

  if (inputFiles) {
    const inputFilesInfo: SubsectionLink[] = [];
    if (Array.isArray(inputFiles)) {
      inputFiles.forEach(file => {
        inputFilesInfo.push({
          unformattedTitle: file['name'],
          link: file['url'],
          linkText: <TruncatedValueTooltip value={file['url']} isUrl={true} />,
        });
      });
      filesSubsections.push({
        infos: inputFilesInfo,
      });
    }
  }

  if (outputFiles) {
    const outputFilesInfo: SubsectionLink[] = [];
    if (Array.isArray(outputFiles)) {
      outputFiles.forEach(file => {
        outputFilesInfo.push({
          unformattedTitle: file['name'],
          link: file['url'],
          linkText: <TruncatedValueTooltip value={file['url']} isUrl={true} />,
        });
      });
    }
    filesSubsections.push({
      infos: outputFilesInfo,
    });
  }

  return {
    title: title,
    subsections: filesSubsections,
  };
};
