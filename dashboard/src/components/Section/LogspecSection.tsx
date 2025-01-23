import type { Dispatch, SetStateAction } from 'react';

import { isStringRecord } from '@/utils/utils';

import type {
  SheetType,
  IJsonContent,
} from '@/components/Sheet/LogOrJsonSheetContent';
import { LogspecInfoIcon } from '@/components/Icons/LogspecInfo';

import { miscContentHandler } from '@/utils/misc';

import type { ISection } from './Section';

export const getLogspecSection = ({
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

  if (!('logspec' in misc) || !isStringRecord(misc.logspec)) {
    return;
  }

  const logspecSection: ISection = {
    title: title,
    icon: <LogspecInfoIcon />,
    subsections: [
      {
        // General subsection
        infos: [],
      },
    ],
  };

  Object.entries(misc.logspec).map(([fieldKey, fieldValue]) => {
    if (typeof fieldValue === 'object' && fieldValue !== null) {
      const subInfos = Object.entries(fieldValue).map(([subKey, subValue]) => {
        const content = miscContentHandler({
          fieldKey: subKey,
          fieldValue: subValue,
          setSheetType: setSheetType,
          setJsonContent: setJsonContent,
        });
        return content;
      });

      logspecSection.subsections?.push({
        title: fieldKey,
        infos: subInfos.filter(info => info !== undefined),
      });
    } else {
      const content = miscContentHandler({
        fieldKey: fieldKey,
        fieldValue: fieldValue,
        setSheetType: setSheetType,
        setJsonContent: setJsonContent,
      });
      if (content !== undefined)
        logspecSection.subsections?.[0].infos.push(content);
    }
  });

  return logspecSection;
};
