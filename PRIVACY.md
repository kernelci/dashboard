# Privacy Policy

This Privacy Policy explains what data the KernelCI Dashboard collects when you
use it, why, and how we protect it. It is written for users of the service.
Operators deploying the Dashboard are responsible for keeping this document
accurate for their own instance and for surfacing it to their users.

## Summary

The KernelCI Dashboard collects **anonymous, aggregate usage analytics** only.
We do **not** build user profiles, do **not** sell data, and do **not** store
any personal identifier.

## What we collect

When you make requests to the Dashboard API (`/api/`), the backend records
aggregate usage metrics. These are stored only as counts (Prometheus counters),
never as per-user records or per-user timestamps:

- **Request attributes**: the API endpoint name, HTTP method, response status
  class (e.g. `2xx`), and coarse client buckets derived from your browser's
  User-Agent (e.g. browser family `Chrome`, operating system `Linux`, device
  type `desktop`). Automated clients are bucketed as `bot`.
- **Referrer domain**: only the external domain that linked you to the
  Dashboard (e.g. `example.org`). Same-site and direct visits are recorded as
  `direct_or_internal`. The full referring URL is never stored.
- **Unique visitor estimates**: daily de-duplicated visit counts, in total and
  per endpoint.

## What we do NOT collect or store

- Your raw IP address.
- Your raw, full User-Agent string.
- The full referrer URL or any query parameters.
- Any account, name, email, or other directly identifying information.
- Any cross-day or long-term tracking identifier.

## How unique visitors are counted

To estimate unique visitors without identifying you, the backend:

1. Computes a one-way fingerprint as
   `HMAC-SHA256(daily_salt, "<your_ip>|<your_user_agent>")`.
2. Uses a `daily_salt` — a random 256-bit secret generated fresh each UTC day,
   held only in an ephemeral cache (Redis/memcached) with a ~25 hour lifetime.
3. Uses only the resulting hash as a short-lived de-duplication key. Your raw
   IP and User-Agent are discarded immediately after the hash is computed and
   are never written to any metric or to disk.

Because the salt is secret and rotates every day, fingerprints cannot be linked
across days, and the hash cannot be reversed back to your IP/User-Agent in
practice.

## Legal basis and retention

- **Purpose**: understanding aggregate usage and load to operate and improve
  the service.
- **Legal basis** (where GDPR applies): legitimate interest in operating and
  improving the service, using the most privacy-preserving design we can.
- **Retention**: the transient daily fingerprints and salt expire automatically
  within ~25 hours. Only anonymous aggregate counters are retained beyond that;
  these contain no personal data.

## Your rights

Because we retain only anonymous, aggregate counts and hold no identifier that
can single you out beyond a single day, we cannot link any stored data to a
specific person and therefore cannot act on individual access/deletion requests
against the aggregate metrics. If you have questions about privacy on a specific
deployment, contact that deployment's operator.

## Data controller and contact

For the upstream instance at
[dashboard.kernelci.org](https://dashboard.kernelci.org), the data controller
is **The Linux Foundation**. For privacy inquiries contact
[privacy@linuxfoundation.org](mailto:privacy@linuxfoundation.org), or write to:

> The Linux Foundation, Attn: Legal Department, 548 Market St, PMB 57274,
> San Francisco, California 94104-5401, USA.

Third-party deployments are controlled by their respective operators, who are
responsible for providing their own contact details.

## Changes

We may update this policy as the service evolves. Changes are tracked in the
repository's git history.

## Technical reference

For implementation details, see
[`docs/monitoring.md`](docs/monitoring.md#client-analytics).
