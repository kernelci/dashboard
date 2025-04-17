import { createFileRoute } from '@tanstack/react-router';

import { ShortTreeLatest } from '@/pages/TreeLatest/ShortTreeLatest';

export const Route = createFileRoute(
  '/_main/(alternatives)/c/$treeName/$branch/',
)({
  component: ShortTreeLatest,
});
