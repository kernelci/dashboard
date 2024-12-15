import qs from 'query-string';

import { type AnySchema, parseSearchWith } from '@tanstack/react-router';

// Must be a character not used in any other query parameters (e.g. '.' or '_' wouldn't work)
const KEY_FLAT_CHAR = '|';
const ARRAY_SEPARATOR = ',';

export const isEncodedJSONArrayParam = (str: string): boolean => {
  // Regex responsible to match URI encoded (or not) array of numbers
  // in the query parameters when they where JSON stringified and not
  // query-string stringified.
  const encodedArrayRegex =
    /=(%5B|\[)\d+(?:(%2C|,)\d+)*(%5D|\])|=(%5B|\[)(%5D|\])/;
  return encodedArrayRegex.test(str);
};

export const parseSearch = (searchStr: string): AnySchema => {
  const JSONChar = '{';
  const encodeJSONChar = encodeURI(JSONChar);
  const encodeKeyFlatChar = encodeURI(KEY_FLAT_CHAR);

  if (
    ((!searchStr.includes(KEY_FLAT_CHAR) ||
      !searchStr.includes(encodeKeyFlatChar)) &&
      (searchStr.includes(JSONChar) || searchStr.includes(encodeJSONChar))) ||
    isEncodedJSONArrayParam(searchStr)
  ) {
    return parseSearchWith(JSON.parse)(searchStr);
  }

  const flattenedParsedSearch = qs.parse(searchStr, {
    arrayFormat: 'bracket-separator',
    arrayFormatSeparator: ARRAY_SEPARATOR,
    parseBooleans: true,
    types: {
      intervalInDays: 'number',
      diffFilter_buildDurationMax: 'number',
      diffFilter_buildDurationMin: 'number',
      diffFilter_bootDurationMin: 'number',
      diffFilter_bootDurationMax: 'number',
      diffFilter_testDurationMin: 'number',
      diffFilter_testDurationMax: 'number',
      treeIndexes: 'number[]',
      startTimestampInSeconds: 'number',
      endTimestampInSeconds: 'number',
    },
  });

  Object.setPrototypeOf(flattenedParsedSearch, Object.prototype);
  const parsedSearch = unflattenObject(flattenedParsedSearch, KEY_FLAT_CHAR);
  return parsedSearch;
};

export const stringifySearch = (
  searchParams: Record<string, unknown>,
): string => {
  const flattenedSearchParams = flattenObject(searchParams, KEY_FLAT_CHAR);
  const stringifiedSearch = qs.stringify(flattenedSearchParams, {
    arrayFormat: 'bracket-separator',
    arrayFormatSeparator: ARRAY_SEPARATOR,
  });
  return stringifiedSearch && `?${stringifiedSearch}`;
};

const isStringRecord = (obj: unknown): obj is Record<string, unknown> => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    !Array.isArray(obj) &&
    Object.keys(obj).every(key => typeof key === 'string')
  );
};

const flattenObject = (
  obj: Record<string, unknown>,
  keySplitChar: string,
  parent = '',
  result: Record<string, boolean | number | string | number[]> = {},
): Record<string, boolean | string | number | number[]> => {
  for (const strKey in obj) {
    const key = strKey as keyof typeof obj;
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = parent ? `${parent}${keySplitChar}${key}` : key;
      if (isStringRecord(obj[key])) {
        flattenObject(obj[key], keySplitChar, newKey, result);
      } else if (
        typeof obj[key] === 'number' ||
        typeof obj[key] === 'string' ||
        typeof obj[key] === 'boolean' ||
        Array.isArray(obj[key])
      ) {
        result[newKey] = obj[key];
      }
    }
  }
  return result;
};

const unflattenObject = (
  obj: qs.ParsedQuery<string | number | boolean>,
  keySplitChar: string,
): Record<string, unknown> => {
  const result: Record<string, unknown> = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const keys = key.split(keySplitChar);
      keys.reduce<Record<string, unknown> | number[]>((acc, part, index) => {
        if (isStringRecord(acc)) {
          if (index === keys.length - 1) {
            acc[part] = obj[key];
          } else {
            acc[part] = acc[part] || {};
          }
          if (isStringRecord(acc[part]) || Array.isArray(acc[part])) {
            return acc[part];
          }
        }
        return acc;
      }, result);
    }
  }
  return result;
};
