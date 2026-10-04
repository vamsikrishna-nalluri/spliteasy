---
id: SE-lockout-001
version: 1.0.0
status: draft
depends_on: [SE-auth-001]
business_goals: [BG-002]
---

# Feature Specification: Account lockout policy after repeated failed logins

**Feature Branch**: `feature/002-account-lockout`

**Created**: 27-Sep-2026

**Input**: User description: An account should be temporarily locked
after too many failed login attempts, to slow down credential-guessing
attacks.

## User Story

### User Story 1 - Account locks after repeated failed attempts (Priority: P2)

After a user (or an attacker) fails to log in too many times in a row,
the account becomes temporarily locked, blocking further login
attempts until the lock naturally expires.

**Why this priority**: Depends on SE-auth-001 existing first (login
must exist before lockout has anything to guard); not required for an
initial login MVP, but needed before the system is exposed beyond
trusted testing.

**Independent Test**: Can be tested by driving 5 consecutive failed
logins against a test account and confirming the account is then
reported as locked, independent of SE-auth-001's own internal login
logic (this spec only needs a "record a failed attempt" and "check
lock state" interface — it does not re-test login itself).

**Scenarios**: SCN-001, SCN-002, SCN-003

---

## Scope

### In scope

- Counting consecutive failed login attempts per account
- Locking an account once the failure threshold is reached
- Defining how and when a lock clears (auto-expiry)

### Out of scope

- The login flow itself, including credential validation (SE-auth-001)
- Manual admin override / unlock (future spec, if needed)
- Notifying the user that their account was locked (future spec)

### Assumptions

- Auto-unlock (time-based expiry) is sufficient for v1; no admin
  manual-unlock capability is required yet.
- Failed-attempt counts are tracked per username, not per IP address,
  in this version.

## Dependencies

- SE-auth-001: this spec attaches lock state to the User entity
  defined there, and SE-auth-001-BR-005 enforces the lock this spec produces. This spec cannot be meaningfully tested end-to-end without
  SE-auth-001's login flow to drive failed attempts through, though
  its own state-machine logic (count, lock, expire) can be unit-tested
  in isolation.

## Business Rules

Money handling: No monetary values.

- **BR-001**: System MUST lock an account after 5 consecutive failed
  login attempts for that username, within a rolling 15-minute window.
- **BR-002**: System MUST automatically clear a lock once the lock
  duration has elapsed, with no manual action required.
- **BR-003**: System MUST reset the consecutive-failure count for a
  username upon a successful login.
- **BR-004**: A failed attempt that falls outside the current
  15-minute rolling window MUST NOT count toward the lockout
  threshold.

### Key Entities *(include if feature involves data)*

- **User** (extends the entity defined in SE-auth-001): additional
  attributes owned by this spec: failed_login_count, locked_until
  (nullable timestamp).

## Scenarios

### Happy path

**SCN-001** (Traces to: BR-003)
- **Given** "alice" has 3 consecutive failed login attempts recorded
- **When** she then submits a successful login
- **Then** her failed_login_count resets to 0

### Failure paths

**SCN-002** (Traces to: BR-001)
- **Given** "alice" has submitted 4 consecutive failed login attempts
  within the last 15 minutes
- **When** she submits a 5th failed attempt
- **Then** her account is locked, with locked_until set 15 minutes
  into the future

### Boundary conditions

**SCN-003** (Traces to: BR-004)
- **Given** "alice" has submitted 4 consecutive failed login attempts,
  the oldest of which occurred 16 minutes ago
- **When** she submits another incorrect password
- **Then** the 16-minute-old attempt has rolled out of the 15-minute
  window, so this counts as her 1st attempt in the current window and
  her account is not locked

**SCN-004** (Traces to: BR-002)
- **Given** "alice"'s account was locked with locked_until set to a
  timestamp that has now passed
- **When** she submits a new login attempt with correct credentials
- **Then** the lock is treated as expired, the login proceeds per
  SE-auth-001's normal rules, and locked_until is cleared

### Verification scenarios

**SCN-005** (Traces to: NFR-001)
- **Given** a login request that requires a lock-state check
- **When** the check is performed as part of the overall login flow
  under the load conditions of SE-auth-001-SCN-008
- **Then** the lock-state check itself contributes no more than 20ms
  at P95 to the total request latency

## Non-Functional Requirements

- **NFR-001**: Lock-state checks (used by SE-auth-001-BR-005) MUST execute in < 20ms at the 95th percentile under normal system load (as part of the overall login latency budget defined in SE-auth-001-NFR-001).

## Traceability Table

| Requirement ID | Description | Business Goal | Scenario(s) | Test(s) |
|---|---|---|---|---|
| SE-lockout-001-BR-001 | Lock after 5 failed attempts / 15 min | BG-002 | SCN-002 | TBD |
| SE-lockout-001-BR-002 | Auto-clear lock after duration elapses | BG-002 | SCN-004 | TBD |
| SE-lockout-001-BR-003 | Reset failure count on success | BG-002 | SCN-001 | TBD |
| SE-lockout-001-BR-004 | Old attempts roll out of rolling window | BG-002 | SCN-003 | TBD |
| SE-lockout-001-NFR-001 | Lock check adds ≤20ms to login latency | BG-002 | SCN-005 | TBD |

## Open Questions

- Is 5 attempts / 15-minute window the right policy for v1, or should
  this be configurable per deployment?
- Should repeated lockouts (e.g. 3 lockouts in 24 hours) escalate to a
  longer lock duration, or stay flat at 15 minutes indefinitely?

## Changelog

- **1.0.0**: Initial draft — extracted from SE-auth-001 to keep login
  and lockout policy independently shippable and versionable.