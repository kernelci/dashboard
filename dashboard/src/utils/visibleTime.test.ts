import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { trackVisibleTime } from './visibleTime';

const BEACON_URL = 'http://localhost:8000/api/analytics/visible/';
const TWENTY_SECONDS_MS = 20_000;
const TWENTY_FIVE_SECONDS_MS = 25_000;
const THIRTY_SECONDS_HIDDEN_MS = 50_000;
const TEN_SECONDS_AFTER_HIDDEN_MS = 60_000;
const ALMOST_ONE_SECOND_MS = 999;
const FIVE_SECONDS_MS = 5_000;
const EIGHT_SECONDS_MS = 8_000;
const ELEVEN_SECONDS_MS = 11_000;
const FIFTEEN_SECONDS_MS = 15_000;
const ONE_HOUR_MS = 3_600_000;
const ONE_DAY_MS = 86_400_000;

type VisibleTimeBody = {
  route: string;
  time_ms: number;
};

const isVisibleTimeBody = (value: unknown): value is VisibleTimeBody => {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  if (!('route' in value) || !('time_ms' in value)) {
    return false;
  }
  return typeof value.route === 'string' && typeof value.time_ms === 'number';
};

describe('trackVisibleTime', () => {
  let clock = 0;
  let visibility: DocumentVisibilityState = 'visible';
  let pathname = '';
  let onResolved: () => void = (): void => {};
  let onVisibility: () => void = (): void => {};
  let onPageShow: (event: { persisted?: boolean }) => void = (): void => {};
  const fetchMock = vi.fn(
    (_url: string, _init?: RequestInit): Promise<Response> =>
      Promise.resolve(new Response()),
  );

  beforeEach(() => {
    clock = 0;
    visibility = 'visible';
    pathname = '/tree/mainline/master/';
    onResolved = (): void => {};
    onVisibility = (): void => {};
    onPageShow = (): void => {};
    fetchMock.mockClear();
    vi.spyOn(performance, 'now').mockImplementation((): number => clock);
    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('document', {
      get visibilityState(): DocumentVisibilityState {
        return visibility;
      },
      addEventListener(type: string, fn: () => void): void {
        if (type === 'visibilitychange') {
          onVisibility = fn;
        }
      },
    });
    vi.stubGlobal('window', {
      addEventListener(
        type: string,
        fn: (event: { persisted?: boolean }) => void,
      ): void {
        if (type === 'pageshow') {
          onPageShow = fn;
        }
      },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  const openRoute = (): void => {
    trackVisibleTime(
      {
        get state() {
          return { location: { pathname } };
        },
        subscribe(_event: 'onResolved', fn: () => void): () => void {
          onResolved = fn;
          return () => undefined;
        },
      },
      BEACON_URL,
    );
    onResolved();
  };

  const body = (call: number): VisibleTimeBody => {
    const init = fetchMock.mock.calls[call]?.[1];
    if (init?.credentials !== 'omit' || typeof init.body !== 'string') {
      throw new Error('missing beacon');
    }
    const parsed: unknown = JSON.parse(init.body);
    if (!isVisibleTimeBody(parsed)) {
      throw new Error('missing beacon');
    }
    return parsed;
  };

  it('sends the visible seconds when the route changes', async () => {
    openRoute();
    clock = TWENTY_SECONDS_MS;
    pathname = '/hardware/board-a/';
    onResolved();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(BEACON_URL);
    expect(body(0)).toEqual({
      route: '/tree/mainline/master',
      time_ms: TWENTY_SECONDS_MS,
    });
  });

  it('does not count time the tab stays hidden', async () => {
    openRoute();
    clock = TWENTY_SECONDS_MS;
    visibility = 'hidden';
    onVisibility();

    expect(body(0)).toMatchObject({
      time_ms: TWENTY_SECONDS_MS,
    });

    clock = THIRTY_SECONDS_HIDDEN_MS;
    visibility = 'visible';
    onVisibility();
    clock = TEN_SECONDS_AFTER_HIDDEN_MS;
    pathname = '/hardware/board-a';
    onResolved();

    expect(body(1)).toEqual({
      route: '/tree/mainline/master',
      time_ms: TEN_SECONDS_AFTER_HIDDEN_MS - THIRTY_SECONDS_HIDDEN_MS,
    });
  });

  it('does not send a zero sample when the path changes while hidden', async () => {
    openRoute();
    clock = TWENTY_SECONDS_MS;
    visibility = 'hidden';
    onVisibility();
    pathname = '/hardware/board-a';
    onResolved();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(body(0)).toEqual({
      route: '/tree/mainline/master',
      time_ms: TWENTY_SECONDS_MS,
    });

    visibility = 'visible';
    onVisibility();
    clock = TWENTY_SECONDS_MS + FIFTEEN_SECONDS_MS;
    pathname = '/labs';
    onResolved();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(body(1)).toEqual({
      route: '/hardware/board-a',
      time_ms: FIFTEEN_SECONDS_MS,
    });
  });

  it('does not send a beacon when only the search changes', async () => {
    openRoute();
    clock = TWENTY_SECONDS_MS;
    onResolved();
    expect(fetchMock).not.toHaveBeenCalled();

    clock = TWENTY_FIVE_SECONDS_MS;
    pathname = '/labs';
    onResolved();
    expect(body(0)).toMatchObject({
      time_ms: TWENTY_FIVE_SECONDS_MS,
    });
  });

  it('sends a stay longer than 24h as measured', async () => {
    openRoute();
    clock = ONE_DAY_MS + ONE_HOUR_MS;
    pathname = '/labs';
    onResolved();
    expect(body(0)).toMatchObject({
      time_ms: ONE_DAY_MS + ONE_HOUR_MS,
    });
  });

  it('sends a visit under 1s', async () => {
    openRoute();
    clock = ALMOST_ONE_SECOND_MS;
    pathname = '/labs';
    onResolved();
    expect(body(0)).toMatchObject({
      time_ms: ALMOST_ONE_SECOND_MS,
    });
  });

  it('starts a new visit after a back-forward cache restore', async () => {
    openRoute();
    clock = FIVE_SECONDS_MS;
    visibility = 'hidden';
    onVisibility();
    expect(body(0)).toMatchObject({ time_ms: FIVE_SECONDS_MS });

    clock = EIGHT_SECONDS_MS;
    visibility = 'visible';
    onPageShow({ persisted: true });
    clock = ELEVEN_SECONDS_MS;
    pathname = '/labs';
    onResolved();
    expect(body(1)).toMatchObject({
      time_ms: ELEVEN_SECONDS_MS - EIGHT_SECONDS_MS,
    });
  });
});
