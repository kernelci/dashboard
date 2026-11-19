import type { Dispatch, SetStateAction } from 'react';

import ReactJsonView from '@microlink/react-json-view';

import { isStringRecord } from '@/utils/utils';

import CopyButton from '@/components/Button/CopyButton';
import type {
  SheetType,
  IJsonContent,
} from '@/components/Sheet/LogOrJsonSheetContent';
import { LogspecInfoIcon } from '@/components/Icons/LogspecInfo';

import { miscContentHandler } from '@/utils/misc';

import type { ISection, SubsectionLink } from './Section';

const logspecField = (
  content: SubsectionLink | undefined,
  key: string,
): SubsectionLink | undefined => {
  if (content === undefined) {
    return;
  }

  switch (key) {
    case 'error_type':
    case 'signature_loc':
      return { ...content, span: 2 };
    case 'script':
    case 'target':
    case 'error_summary':
    case 'src_file':
    case 'hardware':
      return { ...content, span: 4 };
    default:
      return content;
  }
};

const signatureFieldsLink = (value: object): SubsectionLink => ({
  unformattedTitle: 'signature_fields',
  span: 4,
  linkComponent: (
    <div className="flex w-full min-w-0 items-start gap-1">
      <ReactJsonView
        src={value}
        name={false}
        collapsed={0}
        displayDataTypes={false}
        style={{ fontSize: 12 }}
      />
      <CopyButton value={JSON.stringify(value)} />
    </div>
  ),
});

export const getLogspecSection = ({
  misc,
  title,
  parserTitle,
  setSheetType,
  setJsonContent,
}: {
  misc?: object;
  title: string;
  parserTitle?: string;
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
    rightIcon: <LogspecInfoIcon />,
    subsections: [
      {
        title: parserTitle,
        infos: [],
      },
    ],
  };

  Object.entries(misc.logspec).forEach(([fieldKey, fieldValue]) => {
    if (typeof fieldValue === 'object' && fieldValue !== null) {
      const subInfos = Object.entries(fieldValue).map(([subKey, subValue]) => {
        if (
          subKey === 'signature_fields' &&
          subValue !== null &&
          typeof subValue === 'object'
        ) {
          return signatureFieldsLink(subValue);
        }

        const content = miscContentHandler({
          fieldKey: subKey,
          fieldValue: subValue,
          setSheetType: setSheetType,
          setJsonContent: setJsonContent,
        });
        // Object values are already one click away in the JSON sheet; inline text only repeats them.
        const field = logspecField(content, subKey);
        return field?.copyValue ? { ...field, linkText: undefined } : field;
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
      const field = logspecField(content, fieldKey);
      if (field !== undefined) {
        logspecSection.subsections?.[0].infos.push(field);
      }
    }
  });

  return logspecSection;
};
