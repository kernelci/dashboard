type VisibleRouter = {
  state: {
    location: { pathname: string };
  };
  subscribe: (eventType: 'onResolved', fn: () => void) => () => void;
};

const pagePath = (pathname: string): string => {
  if (pathname.length > 1 && pathname.endsWith('/')) {
    return pathname.slice(0, -1);
  }
  return pathname;
};

export const trackVisibleTime = (router: VisibleRouter, url: string): void => {
  let route = '';
  let visibleMs = 0;
  let since = 0;
  let running = false;

  const stop = (): void => {
    if (!running) {
      return;
    }
    visibleMs += performance.now() - since;
    running = false;
  };

  const send = (): void => {
    stop();
    const elapsed = visibleMs;
    visibleMs = 0;
    if (route === '') {
      return;
    }
    const timeMs = Math.round(elapsed);
    // sendBeacon always sends cookies, and this API allows any origin with
    // Access-Control-Allow-Origin: *. A credentialed JSON request is rejected.
    void fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ route, time_ms: timeMs }),
      keepalive: true,
      credentials: 'omit',
    });
  };

  const start = (next: string): void => {
    route = next;
    visibleMs = 0;
    since = performance.now();
    running = next !== '' && document.visibilityState === 'visible';
  };

  router.subscribe('onResolved', () => {
    const next = pagePath(router.state.location.pathname);
    if (next === route) {
      return;
    }
    send();
    start(next);
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      send();
      return;
    }
    if (!running) {
      start(route);
    }
  });

  // A back-forward cache restore can skip visibilitychange.
  window.addEventListener('pageshow', event => {
    if (event.persisted && !running) {
      start(route);
    }
  });
};
