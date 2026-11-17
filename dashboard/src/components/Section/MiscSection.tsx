import { type Dispatch, type SetStateAction } from 'react';

import ReactJsonView from '@microlink/react-json-view';

import CopyButton from '@/components/Button/CopyButton';
import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';
import { isStringRecord } from '@/utils/utils';

import { miscContentHandler } from '@/utils/misc';

import type { ISection, SubsectionLink } from './Section';

const isJsonValue = (
  value: unknown,
): value is Record<string, unknown> | unknown[] =>
  Array.isArray(value) || isStringRecord(value);

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
    .map(([fieldKey, fieldValue]) => {
      if (isJsonValue(fieldValue)) {
        return {
          children: (
            <div className="flex items-start gap-1">
              <ReactJsonView
                src={fieldValue}
                name={fieldKey}
                collapsed={1}
                displayDataTypes={false}
                style={{ fontSize: 12 }}
              />
              <CopyButton value={JSON.stringify(fieldValue)} />
            </div>
          ),
        };
      }

      return miscContentHandler({
        fieldKey: fieldKey,
        fieldValue: fieldValue,
        setSheetType: setSheetType,
        setJsonContent: setJsonContent,
      });
    })
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
