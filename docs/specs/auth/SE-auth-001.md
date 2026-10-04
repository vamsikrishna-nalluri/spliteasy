---
id: SE-auth-001
version: 1.0.0
status: draft
depends_on: []
business_goals: [BG-002]
---

# Feature Specification: User shall be able to login to the spliteasy application

**Feature Branch**: `feature/001-user-login`

**Created**: 27-Sep-2026

**Input**: User description: User should login to the application with a valid username and password

<!--
  Constitution rules that apply to this whole file:
  - Keep the nine "##" sections below, in this order, with these exact names.
  - Module names are singular and registered in the glossary (e.g. `expense`, not `expenses`).
    Confirm [module-name] is in the glossary, or add it there via PR, before merging this spec.
  - IDs: BR-001, NFR-001, SCN-001 (unique within this spec). Qualified references use a
    hyphen: SE-auth-001-BR-001, SE-auth-001-SCN-004.
  - `status` in the frontmatter is one of: draft, in_review, active, deprecated,
    superseded, archived, abandoned.
  - Specs in `in_review` or `active` status must have a scenario for every requirement,
    all three scenario groups populated (or "not applicable" stated), and every row of
    the Traceability Table filled in (TBD allowed only in the Test column).
    Specs in `draft` or `abandoned` status are exempt from these checks.
  - Every `BG-###` in `business_goals` must exist in docs/business-goals.md.
  - `[NEEDS CLARIFICATION: ...]` markers may be used inline, but each one must also be
    listed under Open Questions.
  - Sections with nothing to say contain "None".
-->

## User Story

### User Story 1 - User logs into the SplitEasy application (Priority: P1)

A registered user navigates to the login page, submits their username
and password, and — if the credentials are valid and the account is
not locked — is authenticated and issued a session so they can access
their groups and expenses.

**Why this priority**: Every other operation in the system requires an
authenticated user; nothing else can be built or tested without this.

**Independent Test**: Can be fully tested by submitting a valid
username/password pair and confirming a session token is returned;
delivers value on its own since it is the entry point to the entire
application. The locked-account check can be built and tested against
a stub (a hardcoded "not locked" flag) before SE-lockout-001 exists.

**Scenarios**: SCN-001, SCN-002, SCN-003, SCN-004, SCN-005, SCN-006

---

## Scope

### In scope

- Validating a username/password pair against stored credentials
- Issuing a session token on successful login
- Rejecting invalid credentials (wrong password, unknown username)
- Checking whether an account is currently locked, and rejecting login
  if so

### Out of scope

- Account creation / registration (username and password rules, e.g.
  length and complexity constraints; password hashing algorithm and
  work factor chosen at creation time — belongs to a future
  `SE-registration` spec, not this one)
- What causes an account to become locked, how long a lock lasts, and
  how it clears (belongs to `SE-lockout-001`) — this spec only checks
  and enforces the locked state, it does not define or manage it
- Authorization / permissions — what an authenticated user is allowed
  to do once logged in (future spec)
- Password reset / recovery flow (future spec)

### Assumptions

- We support only the web application; no mobile app in this version.
- Usernames and passwords already exist (created via a registration
  flow not covered here); this spec only validates them.
- Until SE-lockout-001 exists, the locked-state check may be
  implemented as a stub that always returns "not locked."

## Dependencies

- SE-lockout-001: defines what "locked" means (trigger condition,
  duration, unlock condition). Not a hard build dependency — this
  spec can be implemented and shipped against a stub before
  SE-lockout-001 exists — but BR-005's enforcement becomes meaningful
  only once that spec is implemented.

## Business Rules

Money handling: No monetary values.

- **BR-001**: System MUST authenticate a user only when the submitted
  username and password match a stored user record.
- **BR-002**: System MUST issue a session token upon successful
  authentication.
- **BR-003**: System MUST reject login when the password does not
  match the stored value for that username, without revealing whether
  the username itself exists.
- **BR-004**: System MUST reject login when the submitted username
  does not correspond to any stored user record, returning the same
  error response as BR-003 (a generic "invalid credentials" message).
- **BR-005**: System MUST reject a login attempt for an account
  currently in a locked state, regardless of credential correctness,
  per the lockout policy defined in SE-lockout-001.
- **BR-006**: System MUST verify the submitted password by comparing
  it against the stored password hash using the hash's verification
  function; System MUST NOT compare the submitted password as
  plaintext against any stored value.
- **BR-007**: System MUST reject a login attempt with an empty
  username or empty password field before checking against stored
  credentials.

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered account. Key attributes: username
  (unique), password_hash. Lock-state attributes (failed_login_count,
  locked_until) are owned by SE-lockout-001, not this spec.
- **Session**: Represents an active authenticated session. Key
  attributes: token, user reference, issued_at, expires_at.

## Scenarios

### Happy path

**SCN-001** (Traces to: BR-001)
- **Given** a user record exists with username "alice" and a matching
  password hash
- **When** "alice" submits her correct username and password
- **Then** authentication succeeds and a session token is returned

**SCN-002** (Traces to: BR-002)
- **Given** "alice" has just authenticated successfully
- **When** the system issues the response
- **Then** the response includes a session token with a valid
  expiry time

### Failure paths

**SCN-003** (Traces to: BR-003)
- **Given** a user record exists with username "alice"
- **When** "alice" submits her correct username with an incorrect
  password
- **Then** the login is rejected with a generic "invalid credentials"
  error, and no indication that the username was correct

**SCN-004** (Traces to: BR-004)
- **Given** no user record exists with username "nobody"
- **When** a login is submitted with username "nobody" and any
  password
- **Then** the login is rejected with the same generic "invalid
  credentials" error as SCN-003

**SCN-005** (Traces to: BR-007)
- **Given** the login form is submitted
- **When** the username or password field is empty
- **Then** the login is rejected before any credential lookup occurs,
  with a "username and password are required" error

**SCN-006** (Traces to: BR-005)
- **Given** an account currently marked as locked (per
  SE-lockout-001's policy)
- **When** a login is attempted with the correct username and password
- **Then** the login is rejected with an "account locked" error,
  independent of credential correctness

### Boundary conditions
None

### Verification scenarios

**SCN-007** (Traces to: BR-006)
- **Given** a stored password hash for "alice"
- **When** the login handler compares a submitted password against
  the stored hash
- **Then** the comparison uses the hash's verification function (e.g.
  bcrypt-verify), never a plaintext string-equality check, even when
  the submitted password is correct

**SCN-008** (Traces to: NFR-001)
- **Given** 50 concurrent login requests are submitted within the
  same 1-second window
- **When** all 50 are processed
- **Then** the P95 response time across those requests is under 500ms

**SCN-009** (Traces to: NFR-002)
- **Given** "alice" authenticated successfully at time T
- **When** 24 hours have elapsed since T
- **Then** her session token is no longer valid and a protected
  request with it is rejected

## Non-Functional Requirements

- **NFR-001**: Login requests complete in under 500ms at P95 under
  normal load (defined as up to 50 concurrent login requests).
- **NFR-002**: Session tokens expire 24 hours after issuance.

## Traceability Table

| Requirement ID | Description | Business Goal | Scenario(s) | Test(s) |
|---|---|---|---|---|
| SE-auth-001-BR-001 | Authenticate on matching credentials | BG-002 | SCN-001 | TBD |
| SE-auth-001-BR-002 | Issue session token on success | BG-002 | SCN-002 | TBD |
| SE-auth-001-BR-003 | Reject on wrong password, generic error | BG-002 | SCN-003 | TBD |
| SE-auth-001-BR-004 | Reject on unknown username, same generic error | BG-002 | SCN-004 | TBD |
| SE-auth-001-BR-005 | Reject login for a locked account | BG-002 | SCN-006 | TBD |
| SE-auth-001-BR-006 | Verify password via hash comparison, never plaintext | BG-002 | SCN-007 | TBD |
| SE-auth-001-BR-007 | Reject empty username/password before lookup | BG-002 | SCN-005 | TBD |
| SE-auth-001-NFR-001 | Login P95 latency < 500ms | BG-002 | SCN-008 | TBD |
| SE-auth-001-NFR-002 | Session token expires in 24h | BG-002 | SCN-009 | TBD |

## Open Questions

- None

## Changelog

- **1.0.0**: Initial draft — login only. Registration, authorization,
  password reset, and lockout policy (trigger/duration/unlock) are
  explicitly out of scope (separate specs).