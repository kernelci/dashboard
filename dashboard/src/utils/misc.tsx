import type { Dispatch, SetStateAction } from 'react';

import { match, P } from 'ts-pattern';

import { isUrl, shouldTruncate } from '@/lib/string';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';
import type { SubsectionLink } from '@/components/Section/Section';
import { SheetTrigger } from '@/components/Sheet';
import CodeBlock from '@/components/Filter/CodeBlock';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { JsonViewIcon } from '@/components/Icons/JsonView';

import { isStringRecord } from './utils';

export const miscContentHandler = ({
  fieldKey,
  fieldValue,
  setSheetType,
  setJsonContent,
}: {
  fieldKey: string;
  fieldValue: unknown;
  setSheetType?: Dispatch<SetStateAction<SheetType>>;
  setJsonContent?: Dispatch<SetStateAction<IJsonContent | undefined>>;
}): SubsectionLink | undefined => {
  let stringField;

  if (typeof fieldValue?.toString === 'function') {
    stringField = fieldValue.toString();
  } else {
    return;
  }

  const isObjectField = Array.isArray(fieldValue) || isStringRecord(fieldValue);
  if (isObjectField) {
    stringField = JSON.stringify(fieldValue);
  }

  const isUrlResult = isUrl(stringField);
  let children;
  let linkText;

  const showContent = match({ [fieldKey]: fieldValue })
    .with({ log_excerpt: '' }, _ => false)
    .with({ log_excerpt: P.string }, field => {
      children = <CodeBlock code={field.log_excerpt} />;
      return true;
    })
    .otherwise(_ => {
      linkText = !shouldTruncate(stringField) ? (
        stringField
      ) : (
        <TruncatedValueTooltip
          value={stringField}
          isUrl={isUrlResult}
          isClickable={isObjectField}
        />
      );
      return true;
    });

  if (showContent) {
    return {
      unformattedTitle: fieldKey,
      link: isUrlResult ? stringField : undefined,
      icon: isObjectField ? <JsonViewIcon /> : undefined,
      wrapperComponent: isObjectField ? SheetTrigger : undefined,
      onClick: isObjectField
        ? (): void => {
            if (setSheetType !== undefined) {
              setSheetType('json');
            }
            if (setJsonContent !== undefined) {
              setJsonContent({ name: fieldKey, src: fieldValue });
            }
          }
        : undefined,
      copyValue: isObjectField ? stringField : undefined,
      linkText: linkText,
      children: children,
    };
  }
};
