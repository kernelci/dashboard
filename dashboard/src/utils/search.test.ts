import { describe, it, expect, assert } from 'vitest';

import { stringifySearchWith } from '@tanstack/react-router';

import {
  flattenObject,
  unflattenObject,
  parseSearch,
  stringifySearch,
  isEncodedJSONArrayParam,
  minifyParams,
  unminifyParams,
} from './search';

const KEY_FLAT_CHAR = '|';

const simpleObject = {
  origin: 'maestro',
  intervalInDays: 7,
  // eslint-disable-next-line no-magic-numbers
  treeIndexes: [1, 2, 3],
};

const simpleObjectMinify = {
  o: 'maestro',
  i: 7,
  // eslint-disable-next-line no-magic-numbers
  x: [1, 2, 3],
};

const simpleObjectStringify = '?o=maestro&i=7&x[]=1,2,3';

const nestedObject = {
  origin: 'maestro',
  intervalInDays: 7,
  tableFilter: {
    bootsTable: 'all',
    buildsTable: 'failed',
    testsTable: 'all',
  },
  treeInfo: {
    treeName: 'android',
    headCommitHash: 'hash',
  },
  diffFilter: {
    configs: { defconfig: true },
    archs: { arm: true },
    testPath: 'amlogic',
  },
  treeIndexes: [0, 1, 2],
};

const nestedObjectMinify = {
  o: 'maestro',
  i: 7,
  tf: {
    bt: 'a',
    b: 'f',
    t: 'a',
  },
  tri: {
    t: 'android',
    ch: 'hash',
  },
  df: {
    c: { defconfig: true },
    a: { arm: true },
    tp: 'amlogic',
  },
  x: [0, 1, 2],
};

const nestedObjectStringify =
  '?o=maestro&i=7' +
  '&tf|bt=a&tf|b=f&tf|t=a' +
  '&tri|t=android&tri|ch=hash' +
  '&df|c|defconfig=true&df|a|arm=true&df|tp=amlogic' +
  '&x[]=0,1,2';

const flatObject = {
  origin: 'maestro',
  intervalInDays: 7,
  'tableFilter|bootsTable': 'all',
  'tableFilter|buildsTable': 'failed',
  'tableFilter|testsTable': 'all',
  'treeInfo|treeName': 'android',
  'treeInfo|headCommitHash': 'hash',
  'diffFilter|configs|defconfig': true,
  'diffFilter|archs|arm': true,
  'diffFilter|testPath': 'amlogic',
  treeIndexes: [0, 1, 2],
};

const flatObjectMinify = {
  o: 'maestro',
  i: 7,
  'tf|bt': 'a',
  'tf|b': 'f',
  'tf|t': 'a',
  'tri|t': 'android',
  'tri|ch': 'hash',
  'df|c|defconfig': true,
  'df|a|arm': true,
  'df|tp': 'amlogic',
  x: [0, 1, 2],
};

describe('isEncodedArrayParam', () => {
  const emptyJSONArrayStr = 'treeIndexes=[]';
  const emptyQSArrayStr = 'treeIndexes[]';
  const filledJSONArrayStr = 'treeIndexes=[1,2,3]';
  const filledQSArrayStr = 'treeIndexes[]=1,2,3';

  it('JSON empty array', () => {
    expect(isEncodedJSONArrayParam(emptyJSONArrayStr)).toBe(true);
  });

  it('JSON empty array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(emptyJSONArrayStr))).toBe(true);
  });

  it('query-string empty array', () => {
    expect(isEncodedJSONArrayParam(emptyQSArrayStr)).toBe(false);
  });

  it('query-string empty array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(emptyQSArrayStr))).toBe(false);
  });

  it('JSON filled array', () => {
    expect(isEncodedJSONArrayParam(filledJSONArrayStr)).toBe(true);
  });

  it('JSON filled array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(filledJSONArrayStr))).toBe(true);
  });

  it('JSON filled array - partially URI encoded', () => {
    const customEncodedStr = filledJSONArrayStr.replace(/,/g, '%2C');
    expect(isEncodedJSONArrayParam(customEncodedStr)).toBe(true);
  });

  it('query-string filled array', () => {
    expect(isEncodedJSONArrayParam(filledQSArrayStr)).toBe(false);
  });

  it('query-string filled array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(filledQSArrayStr))).toBe(false);
  });
});

describe('flattenObject', () => {
  it('Simple object with filled array', () => {
    expect(flattenObject(simpleObject, KEY_FLAT_CHAR)).toStrictEqual(
      simpleObject,
    );
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    expect(flattenObject(simpleObjectEmptyArray, KEY_FLAT_CHAR)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('Nested object', () => {
    expect(flattenObject(nestedObject, KEY_FLAT_CHAR)).toStrictEqual(
      flatObject,
    );
  });
});

describe('unflattenObject', () => {
  it('Simple object with filled array', () => {
    expect(unflattenObject(simpleObject, KEY_FLAT_CHAR)).toStrictEqual(
      simpleObject,
    );
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    expect(
      unflattenObject(simpleObjectEmptyArray, KEY_FLAT_CHAR),
    ).toStrictEqual(simpleObjectEmptyArray);
  });

  it('Nested object', () => {
    expect(unflattenObject(flatObject, KEY_FLAT_CHAR)).toStrictEqual(
      nestedObject,
    );
  });
});

describe('minifyParams', () => {
  it('Simple object with filled array', () => {
    expect(minifyParams(simpleObject)).toStrictEqual(simpleObjectMinify);
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const simpleObjectEmptyArrayMinify = { ...simpleObjectMinify, x: [] };
    expect(minifyParams(simpleObjectEmptyArray)).toStrictEqual(
      simpleObjectEmptyArrayMinify,
    );
  });

  it('Nested object', () => {
    expect(minifyParams(nestedObject)).toStrictEqual(nestedObjectMinify);
  });
});

describe('unminifyParams', () => {
  it('Simple object with filled array', () => {
    expect(unminifyParams(simpleObjectMinify)).toStrictEqual(simpleObject);
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const simpleObjectEmptyArrayMinify = { ...simpleObjectMinify, x: [] };
    expect(unminifyParams(simpleObjectEmptyArrayMinify)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('Nested object', () => {
    expect(unminifyParams(nestedObjectMinify)).toStrictEqual(nestedObject);
  });
});

describe('parseSearch', () => {
  it('Simple object with filled array', () => {
    expect(parseSearch(simpleObjectStringify)).toStrictEqual(simpleObject);
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const simpleObjectEmptyArrayStringify = '?o=maestro&i=7&x[]';
    expect(parseSearch(simpleObjectEmptyArrayStringify)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('Nested object', () => {
    expect(parseSearch(nestedObjectStringify)).toStrictEqual(nestedObject);
  });

  it('Simple object with filled array - URI encoded', () => {
    expect(parseSearch(encodeURI(simpleObjectStringify))).toStrictEqual(
      simpleObject,
    );
  });

  it('Nested object - URI encoded', () => {
    expect(parseSearch(encodeURI(nestedObjectStringify))).toStrictEqual(
      nestedObject,
    );
  });

  it('JSON stringified simple object with filled array', () => {
    const JSONSimpleObjectStringify = stringifySearchWith(JSON.stringify)(
      simpleObject,
    );
    expect(parseSearch(JSONSimpleObjectStringify)).toStrictEqual(simpleObject);
  });

  it('JSON stringified simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const JSONSimpleObjectStringify = stringifySearchWith(JSON.stringify)(
      simpleObjectEmptyArray,
    );
    expect(parseSearch(JSONSimpleObjectStringify)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('JSON stringified simple object - not URI encoded', () => {
    const JSONSimpleObjectStringify = stringifySearchWith(JSON.stringify)(
      simpleObject,
    );
    const decodeStr = JSONSimpleObjectStringify.replace(/%5B/g, '[').replace(
      /%5D/g,
      ']',
    );
    expect(parseSearch(decodeStr)).toStrictEqual(simpleObject);
  });

  it('JSON stringified nested object', () => {
    const JSONNestedObjectStringify = stringifySearchWith(JSON.stringify)(
      nestedObject,
    );
    expect(parseSearch(JSONNestedObjectStringify)).toStrictEqual(nestedObject);
  });
});

describe('stringifySearch', () => {
  const assertSearchParams = (
    result: string,
    expected: Record<string, unknown>,
  ): void => {
    assert(result.includes('?'));
    for (const [key, value] of Object.entries(expected)) {
      if (Array.isArray(value)) {
        const arrayKeyStr = `${encodeURIComponent(key)}[]`;
        const arrayValueStr = `${value.length !== 0 ? '=' + value.join(',') : ''}`;
        assert(result.includes(`${arrayKeyStr}${arrayValueStr}`));
      } else {
        const valueStr = `${encodeURIComponent(key)}=${value}`;
        assert(result.includes(valueStr));
      }
    }
  };

  it('Simple object with filled array', () => {
    const result = stringifySearch(simpleObject);
    assertSearchParams(result, simpleObjectMinify);
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const simpleObjectEmptyArrayMinify = { ...simpleObjectMinify, x: [] };
    const result = stringifySearch(simpleObjectEmptyArray);
    assertSearchParams(result, simpleObjectEmptyArrayMinify);
  });

  it('Nested object', () => {
    const result = stringifySearch(nestedObject);
    assertSearchParams(result, flatObjectMinify);
  });
});
