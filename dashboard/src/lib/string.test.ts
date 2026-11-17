import { describe, expect, it } from 'vitest';

import { isHttpUrl } from './string';

describe('isHttpUrl', () => {
  it('accepts absolute http and https URLs', () => {
    expect(isHttpUrl('https://lore.kernel.org/all/')).toBe(true);
    expect(isHttpUrl('http://example.com')).toBe(true);
  });

  it('rejects placeholders, relative paths, and other protocols', () => {
    expect(isHttpUrl('-')).toBe(false);
    expect(isHttpUrl('/tree/mainline')).toBe(false);
    expect(isHttpUrl('javascript:alert(1)')).toBe(false);
    expect(isHttpUrl('https://')).toBe(false);
  });
});
