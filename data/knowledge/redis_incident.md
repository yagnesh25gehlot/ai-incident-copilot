# INC-REDIS-7421

Service: session-service
Component: Redis
Severity: high

## Incident

Users were unexpectedly logged out of active sessions.

The session service could not reliably communicate with Redis.
Application logs contained repeated Redis connection timeout errors.

## Root Cause

Redis reached its memory limit and started rejecting writes.
Session updates therefore failed.

## Resolution

Memory usage was reduced and Redis capacity was increased.
The session service recovered after Redis became writable again.

## Prevention

Monitor Redis memory utilization and rejected writes.
Configure alerts before memory usage approaches the configured limit.