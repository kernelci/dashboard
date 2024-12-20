import { isUrl, shouldTruncate } from '@/lib/string';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import type { ISection, SubsectionLink } from './Section';

export const getMiscSection = ({
  misc,
  title,
}: {
  misc?: object;
  title: string;
}): ISection | undefined => {
  if (!misc || Object.keys(misc).length === 0) {
    return;
  }

  const miscInfos: SubsectionLink[] = Object.entries(misc).map(
    ([fieldKey, fieldValue]) => {
      let stringField = fieldValue.toString();
      if (typeof fieldValue === 'object') {
        stringField = JSON.stringify(fieldValue);
      }
      const isUrlResult = isUrl(stringField);

      if (!shouldTruncate(stringField)) {
        return {
          key: fieldKey,
          unformattedTitle: fieldKey,
          linkText: stringField,
          link: isUrlResult ? stringField : undefined,
        };
      }

      return {
        key: fieldKey,
        unformattedTitle: fieldKey,
        linkText: (
          <TruncatedValueTooltip value={stringField} isUrl={isUrlResult} />
        ),
        link: isUrlResult ? stringField : undefined,
      };
    },
  );

  return {
    title: title,
    subsections: [
      {
        infos: miscInfos,
      },
    ],
  };
};
