import { describe, expect, it } from 'vitest';
import type { ZodTypeAny } from 'zod';

import { Route } from '@/routes/_main/hardware/$hardwareId/route';
import { DEFAULT_HARDWARE_DIFF_FILTER } from '@/types/general';

const schema = Route.options.validateSearch as ZodTypeAny;

describe('hardware details search', () => {
  it('maps a legacy origin to the test origin filter', () => {
    const { diffFilter, ...search } = schema.parse({
      origin: 'microsoft',
      diffFilter: { configs: { defconfig: true } },
    });
    expect(search).not.toHaveProperty('origin');
    expect(diffFilter).toEqual({
      configs: { defconfig: true },
      testOrigin: { microsoft: true },
    });
  });

  it('keeps the listing defaults for the root default origin', () => {
    expect(schema.parse({ origin: 'maestro' }).diffFilter).toEqual(
      DEFAULT_HARDWARE_DIFF_FILTER,
    );
    expect(schema.parse({}).diffFilter).toEqual(DEFAULT_HARDWARE_DIFF_FILTER);
  });
});
