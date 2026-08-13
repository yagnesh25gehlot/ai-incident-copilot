# TLS Certificate Failure Runbook

Service: api-gateway
Component: TLS

## Symptoms

Clients cannot establish secure connections with the API gateway.
TLS handshakes fail and clients may report certificate validation errors.

## Diagnosis

Inspect the server certificate expiration date.
Verify the certificate hostname matches the requested hostname.
Check the certificate chain and issuing certificate authority.

## Root Cause

A common cause is an expired server certificate or an invalid
certificate chain.

## Resolution

Replace the expired or invalid certificate with a valid certificate
and restart or reload the affected gateway service if required.

## Prevention

Monitor certificate expiration dates and alert well before expiry.