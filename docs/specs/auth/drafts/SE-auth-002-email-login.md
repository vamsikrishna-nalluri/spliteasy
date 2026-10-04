---
id: SE-auth-002
version: 1.0.0
status: draft
depends_on: []
business_goals: [BG-002]
---

# Feature Specification: User shall be able to login with an email address (v2)

**Feature Branch**: `feature/005-email-login`
**Created**: 28-Sep-2026
**Input**: User description: Login must require a valid email address instead of a username to prepare for password recovery features.

> **Migration Required: Deprecation of Username Login (SE-auth-001)**
> 
> **What is changing:** The authentication system (`SE-auth-001`) is being replaced by this spec (`SE-auth-002`). Users must now log in using their registered `email` address instead of a `username`.
> **Why:** To guarantee global identity uniqueness and prepare the system for the upcoming password recovery module.
> **Action Required (Web Team):** Update frontend payloads.
> *Before (v1):* `{"username": "alice", "password": "..."}`
> *After (v2):* `{"email": "alice@example.com", "password": "..."}`

## User Story

### User Story 1 - User logs in with email (Priority: P1)

A registered user navigates to the login page, submits their email address and password, and if valid, is authenticated and issued a session.

## Scope

### In scope
- Validating an email/password pair against stored credentials.
- Issuing a session token on successful login.
- Rejecting invalid formats (non-RFC 5322 emails).

### Out of scope
- Account creation / registration.
- Password reset / recovery flow.

### Assumptions
- User emails and passwords already exist in the database.

## Dependencies

- **SE-lockout-001**: Defines lock state. (Requires an immediate patch to track by email instead of username).

### Impact Map (v1 to v2 Migration)
| Dependency Type | System / Component | Impact of Change | Required Action |
|---|---|---|---|
| **Downstream** | Web UI Client | Login form currently expects a "Username" field. | Web team must update the UI label to "Email" and update JSON payload key to `email`. |
| **Downstream** | `SE-lockout-001` | Tracks failed attempts by `username`. | Generate a patch for `SE-lockout-001` changing the tracking key to `email`. |
| **Upstream** | Registration API | Must guarantee email uniqueness instead of username uniqueness. | Note for the future `SE-registration` spec to index on the email column. |

## Business Rules

Money handling: No monetary values.

- **BR-001**: System MUST authenticate a user only when the submitted email and password match a stored user record.
- **BR-002**: System MUST issue a session token upon successful authentication.
- **BR-003**: System MUST reject login when the password does not match.
- **BR-004**: System MUST reject login when the submitted email does not correspond to any stored user record.
- **BR-005**: System MUST reject a login attempt for an account currently in a locked state.
- **BR-006**: System MUST verify the submitted password by comparing it against the stored password hash using the verification function.
- **BR-007**: System MUST reject a login attempt with an empty email or password field.
- **BR-008**: System MUST reject login attempts where the email does not conform to standard RFC 5322 format before checking the database.

## Scenarios

### Happy path

**SCN-001** (Traces to: BR-001)
- **Given** a user record exists with email "alice@example.com"
- **When** she submits her correct email and password
- **Then** authentication succeeds and a session token is returned

**SCN-002** (Traces to: BR-002)
- **Given** "alice@example.com" has just authenticated successfully
- **When** the system issues the response
- **Then** the response includes a session token

### Failure paths

**SCN-003** (Traces to: BR-003)
- **Given** a user record exists with email "alice@example.com"
- **When** she submits her correct email with an incorrect password
- **Then** the login is rejected with an "invalid credentials" error

**SCN-004** (Traces to: BR-004)
- **Given** no user record exists with email "nobody@example.com"
- **When** a login is submitted with that email
- **Then** the login is rejected with an "invalid credentials" error

**SCN-005** (Traces to: BR-007)
- **Given** the login form is submitted
- **When** the email or password field is empty
- **Then** the login is rejected with a required field error

**SCN-006** (Traces to: BR-005)
- **Given** an account currently marked as locked
- **When** a login is attempted with the correct email and password
- **Then** the login is rejected with an "account locked" error

**SCN-007** (Traces to: BR-008)
- **Given** the login form is submitted
- **When** the email provided is "alice.at.example.com" (invalid format)
- **Then** the login is rejected with a format error before DB lookup

### Boundary conditions
None

### Verification scenarios

**SCN-008** (Traces to: BR-006)
- **Given** a stored password hash for "alice@example.com"
- **When** the login handler compares a submitted password
- **Then** the comparison uses the hash's verification function

## Non-Functional Requirements

- **NFR-001**: Login requests complete in under 500ms at P95 under normal load.
- **NFR-002**: Session tokens expire 24 hours after issuance.

## Traceability Table

| Requirement ID | Description | Business Goal | Scenario(s) | Test(s) |
|---|---|---|---|---|
| SE-auth-002-BR-001 | Authenticate on matching email/password | BG-002 | SCN-001 | TBD |
| SE-auth-002-BR-002 | Issue session token | BG-002 | SCN-002 | TBD |
| SE-auth-002-BR-003 | Reject wrong password | BG-002 | SCN-003 | TBD |
| SE-auth-002-BR-004 | Reject unknown email | BG-002 | SCN-004 | TBD |
| SE-auth-002-BR-005 | Reject locked account | BG-002 | SCN-006 | TBD |
| SE-auth-002-BR-006 | Verify via hash compare | BG-002 | SCN-008 | TBD |
| SE-auth-002-BR-007 | Reject empty fields | BG-002 | SCN-005 | TBD |
| SE-auth-002-BR-008 | Reject invalid RFC 5322 email formats | BG-002 | SCN-007 | TBD |
| SE-auth-002-NFR-001 | Login P95 < 500ms | BG-002 | None | TBD |
| SE-auth-002-NFR-002 | Token expires in 24h | BG-002 | None | TBD |

## Open Questions

None

## Changelog

- **1.0.0**: Initial draft. Supersedes SE-auth-001 by moving from username to email-based authentication.