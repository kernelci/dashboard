import { type Dispatch, type SetStateAction } from 'react';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';

import { miscContentHandler } from '@/utils/misc';

import type { ISection, SubsectionLink } from './Section';

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

  const miscInfos: SubsectionLink[] = Object.entries(misc)
    .map(([fieldKey, fieldValue]) =>
      miscContentHandler({
        fieldKey: fieldKey,
        fieldValue: fieldValue,
        setSheetType: setSheetType,
        setJsonContent: setJsonContent,
      }),
    )
    .filter(info => info !== undefined);

  return {
    title: title,
    subsections: [
      {
        infos: miscInfos,
      },
    ],
  };
};
