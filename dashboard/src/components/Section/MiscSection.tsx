import { type Dispatch, type SetStateAction } from 'react';

import { MdFolderOpen } from 'react-icons/md';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';

import { isUrl, shouldTruncate } from '@/lib/string';

import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';

import { SheetTrigger } from '@/components/Sheet';

import type { ISection, SubsectionLink } from './Section';

const BlueFolderIcon = (): JSX.Element => (
  <MdFolderOpen className="text-blue" />
);

export const getMiscSection = ({
  misc,
  title,
  setSheetType,
  setJsonContent,
}: {
  misc?: object;
  title: string;
  setSheetType?: Dispatch<SetStateAction<SheetType>>;
  setJsonContent?: Dispatch<SetStateAction<IJsonContent | undefined>>;
}): ISection | undefined => {
  if (!misc || Object.keys(misc).length === 0) {
    return;
  }

  const miscInfos: SubsectionLink[] = Object.entries(misc).map(
    ([fieldKey, fieldValue]) => {
      let stringField = fieldValue.toString();
      let isObjectField = false;
      if (typeof fieldValue === 'object') {
        stringField = JSON.stringify(fieldValue);
        isObjectField = true;
      }
      const isUrlResult = isUrl(stringField);

      if (!shouldTruncate(stringField)) {
        return {
          key: fieldKey,
          unformattedTitle: fieldKey,
          linkText: stringField,
          link: isUrlResult ? stringField : undefined,
          icon: isObjectField ? <BlueFolderIcon /> : undefined,
          wrapperComponent: isObjectField ? SheetTrigger : undefined,
          onClick: isObjectField
            ? (): void => {
                if (setSheetType !== undefined) setSheetType('json');
                if (setJsonContent !== undefined)
                  setJsonContent({ name: fieldKey, src: fieldValue });
              }
            : undefined,
          copyValue: isObjectField ? stringField : undefined,
        };
      }

      return {
        key: fieldKey,
        unformattedTitle: fieldKey,
        linkText: (
          <TruncatedValueTooltip value={stringField} isUrl={isUrlResult} />
        ),
        icon: isObjectField ? <BlueFolderIcon /> : undefined,
        wrapperComponent: isObjectField ? SheetTrigger : undefined,
        onClick: isObjectField
          ? (): void => {
              if (setSheetType !== undefined) setSheetType('json');
              if (setJsonContent !== undefined)
                setJsonContent({ name: fieldKey, src: fieldValue });
            }
          : undefined,
        link: isUrlResult ? stringField : undefined,
        copyValue: isObjectField ? stringField : undefined,
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
