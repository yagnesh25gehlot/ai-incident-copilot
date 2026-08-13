# PostgreSQL Connection Pool Runbook

Service: payment-api
Component: PostgreSQL
Owner: Payments Platform

## Symptoms

When the PostgreSQL connection pool becomes exhausted,
payment API requests begin waiting for available database connections.
Requests eventually time out and users may receive HTTP 500 errors.

## Diagnosis

Check the application's active connection count and configured pool size.
Inspect PostgreSQL active connections and max_connections.
Look for long-running queries or connections that are not being released.

## Root Cause

Connection pool exhaustion can occur because of a traffic spike,
slow database queries, or leaked application connections.

## Resolution

Identify and terminate abnormal long-running queries if safe.
Restart unhealthy application workers when connections are leaked.
Increase the application connection pool only after verifying that
PostgreSQL has enough capacity.

## Prevention

Monitor connection-pool utilization, database connection count,
query latency, and request timeout rate.