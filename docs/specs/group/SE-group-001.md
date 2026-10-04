---
id: SE-group-001
version: 1.2.0
status: draft
depends_on: [SE-auth-001]
business_goals: [BG-001, BG-002]
---

# Feature Specification: User shall be able to create and name a group, with optional description

**Feature Branch**: `feature/003-create-group` and `feature/004-group-description`

**Created**: 27-Sep-2026

**Input**: 
- v1.0.0: User description: An authenticated user should be able to create a group, becoming its sole admin, and later rename it.
- v1.1.0 [DELTA]: User description: Allow users to optionally provide a group description at creation time.

<!--
  Constitution rules that apply to this whole file:
  - Keep the nine "##" sections below, in this order, with these exact names.
  - Module names are singular and registered in the glossary (e.g. `expense`, not `expenses`).
    Confirm [module-name] is in the glossary, or add it there via PR, before merging this spec.
  - IDs: BR-001, NFR-001, SCN-001 (unique within this spec). Qualified references use a
    hyphen: SE-group-001-BR-001, SE-group-001-SCN-004.
  - `status` in the frontmatter is one of: draft, in_review, active, deprecated,
    superseded, archived, abandoned.
  - Specs in `in_review` or `active` status must have a scenario for every requirement,
    all four scenario groups populated (or "not applicable" stated), and every row of
    the Traceability Table filled in (TBD allowed only in the Test column).
    Specs in `draft` or `abandoned` status are exempt from these checks.
  - Every `BG-###` in `business_goals` must exist in docs/business-goals.md.
  - `[NEEDS CLARIFICATION: ...]` markers may be used inline, but each one must also be
    listed under Open Questions.
  - Sections with nothing to say contain "None".
-->

## User Story

### User Story 1 - User creates a group and becomes its admin (Priority: P1)

An authenticated user creates a new group by giving it a name. The
creator is automatically added as a member and set as the group's
sole admin. The admin can later edit the group's name.

**Why this priority**: A group is the container for all shared-expense
activity; nothing in `expense` or `settlement` can exist without a
group to belong to.

**Independent Test**: Can be fully tested by an authenticated user
submitting a group name and confirming a group is created with that
user as its only member and admin, independent of any other module
(no expense or membership-management behavior required to verify
this).

**Scenarios**: SCN-001, SCN-002, SCN-003, SCN-013

---

### User Story 2 - Group Description [DELTA v1.1.0] (Priority: P2)

Update to the existing group creation flow (Baseline v1.0.0): The admin can optionally set a plain-text description when creating a group, and can edit it later.

**Why this priority**: Group descriptions help members understand the group's purpose and context without requiring external documentation.

**Independent Test**: Can be fully tested by an authenticated user creating a group with an optional description and confirming it is saved, and by the admin editing the description.

**Scenarios**: SCN-017, SCN-018

---

## Scope

### In scope

- Creating a group (authenticated user only)
- Assigning the creator as the group's sole member and admin at
  creation
- Editing the group's name (admin only)
- Accepting an optional group description at creation [DELTA v1.1.0]
- Editing the group description (admin only) [DELTA v1.1.0]
- Accepting an optional default currency (3-letter ISO 4217 code) at creation, defaulting to 'USD' if omitted [DELTA v1.1.1]

### Out of scope

- Adding or removing members after creation (future spec)
- Reassigning admin to another member, and admin leaving the group
  (future spec — leaving requires reassignment, which is out of
  scope here)
- Group deletion (future spec, if needed)
- Expense-sharing behavior — being a member of a group does not by
  itself determine how expenses are shared or visible to that member;
  that is governed by SE-expense-001, not this spec
- Formatting or rich-text (Markdown/HTML) within the description [DELTA v1.1.0]

### Assumptions

- Being a member of a group does not automatically share any expense
  with that member; expense visibility and splitting are defined
  entirely by SE-expense-001.
- A group with only its creator/admin as a member (no other members
  added) is a valid, persisted state, not an error.
- The letters/digits/spaces-only restriction (BR-010) is a deliberate
  v1 simplification, not a permanent design decision. Relaxing it
  (e.g. allowing emoji or extended punctuation) is expected to arrive
  as a future minor-version delta on this spec, not a new module.
  
## Dependencies

- SE-auth-001: group creation and name-editing both require an
  authenticated user; this spec relies on SE-auth-001's session/user
  identity to determine who is creating or editing a group.

## Business Rules

Money handling: The group maintains a default currency (3-letter ISO 4217 code) that serves as the base ledger currency for all expense tracking and settlement within the group.

- **BR-001**: System MUST allow only an authenticated user to create
  a group.
- **BR-002**: System MUST require a non-empty group name at creation,
  no longer than 20 characters.
- **BR-003**: System MUST allow multiple groups to share the same
  name; group names are not required to be unique.
- **BR-004**: System MUST automatically add the creator of a group as
  a member of that group at creation time.
- **BR-005**: System MUST designate the creator as the sole admin of
  the group at creation time.
- **BR-006**: A group MUST have exactly one admin at all times; this
  spec defines no mechanism to change who holds that role.
- **BR-007**: A newly created group MAY have no members other than
  the creator/admin (i.e. "empty" means no additional members, not
  zero members — the creator is always present).
- **BR-008**: System MUST allow only the current admin to edit the
  group's name after creation.
- **BR-009**: An edited group name MUST also be non-empty and no
  longer than 20 characters, per BR-002.
- **BR-010**: A group name MUST contain only letters, digits, and
  spaces; no emoji, punctuation, or other special characters are
  permitted, at creation or when edited.
- **BR-011**: System MUST accept an optional group description at creation, up to 255 characters. [DELTA v1.1.0]
- **BR-012**: System MUST allow the current admin to edit the description after creation. [DELTA v1.1.0]
- **BR-013**: System MUST accept an optional default_currency field at group creation, specified as a 3-letter ISO 4217 code. [DELTA v1.2.0]
- **BR-014**: If no currency is provided at creation, the system MUST default to 'USD'. [DELTA v1.2.0]


### Key Entities *(include if feature involves data)*

- **Group**: Represents a shared-expense group. Key attributes:
  name (non-empty, ≤20 characters, not unique), admin (reference to
  a single User, set at creation), members (a set of Users, including
  the admin), description (optional plain-text, ≤255 characters) [DELTA v1.1.0], default_currency (optional 3-letter ISO 4217 code, defaults to 'USD') [DELTA v1.1.1].

## Scenarios

### Happy path

**SCN-001** (Traces to: BR-001)
- **Given** an authenticated user "alice"
- **When** she submits a request to create a group named "Roommates"
- **Then** a new group is created

**SCN-002** (Traces to: BR-004)
- **Given** "alice" has just created the group "Roommates"
- **When** the group is persisted
- **Then** "alice" is included in the group's member list

**SCN-003** (Traces to: BR-005)
- **Given** "alice" has just created the group "Roommates"
- **When** the group is persisted
- **Then** "alice" is recorded as the group's sole admin

**SCN-004** (Traces to: BR-008)
- **Given** "alice" is the admin of "Roommates"
- **When** she submits a request to rename it to "Flatmates"
- **Then** the group's name is updated to "Flatmates"

**SCN-013** (Traces to: BR-003)
- **Given** a group named "Roommates" already exists, created by
  "alice"
- **When** "bob" creates a new, separate group also named "Roommates"
- **Then** both groups are created successfully as distinct groups
  sharing the same name

**SCN-017** (Traces to: BR-011) [DELTA v1.1.0]
- **Given** an authenticated user "alice"
- **When** she creates a group with a valid 255-character description
- **Then** the group is created and the description is saved

**SCN-018** (Traces to: BR-012) [DELTA v1.1.0]
- **Given** "alice" is the admin of the group
- **When** she submits a request to edit the description
- **Then** the description is updated successfully

**SCN-019** (Traces to: BR-013) [DELTA v1.1.1]
- **Given** an authenticated user "alice"
- **When** she creates a group specifying a valid currency code (e.g., 'EUR')
- **Then** the group is created and the currency is saved as the default_currency

**SCN-020** (Traces to: BR-014) [DELTA v1.1.1]
- **Given** an authenticated user "alice"
- **When** she creates a group without specifying a currency
- **Then** the group is created with 'USD' as the default_currency

### Failure paths

**SCN-005** (Traces to: BR-001)
- **Given** an unauthenticated request (no valid session)
- **When** a request to create a group is submitted
- **Then** the request is rejected and no group is created

**SCN-006** (Traces to: BR-002)
- **Given** an authenticated user "alice"
- **When** she submits a request to create a group with an empty name
- **Then** the request is rejected with a "group name is required"
  error and no group is created

**SCN-007** (Traces to: BR-008)
- **Given** "alice" is the admin of "Roommates" and "carol" is a
  member but not the admin
- **When** "carol" submits a request to rename the group
- **Then** the request is rejected with an authorization error and
  the group's name is unchanged

**SCN-008** (Traces to: BR-009)
- **Given** "alice" is the admin of "Roommates"
- **When** she submits a rename request with an empty name
- **Then** the request is rejected with a "group name is required"
  error and the group's name is unchanged
**SCN-015** (Traces to: BR-010)
- **Given** an authenticated user "alice"
- **When** she attempts to create a group named "Roomies 🏠"
- **Then** the request is rejected with an "invalid characters in
  group name" error and no group is created

**SCN-016** (Traces to: BR-010)
- **Given** "alice" is the admin of "Roommates"
- **When** she attempts to rename it to "Flat-mates!"
- **Then** the request is rejected with an "invalid characters in
  group name" error and the group's name is unchanged

### Boundary conditions

**SCN-009** (Traces to: BR-002)
- **Given** an authenticated user "alice"
- **When** she creates a group with a name exactly 20 characters long
- **Then** the group is created successfully

**SCN-010** (Traces to: BR-002)
- **Given** an authenticated user "alice"
- **When** she attempts to create a group with a name 21 characters
  long
- **Then** the request is rejected with a "group name too long" error

**SCN-011** (Traces to: BR-009)
- **Given** "alice" is the admin of "Roommates"
- **When** she renames it to a name exactly 20 characters long
- **Then** the rename succeeds

**SCN-012** (Traces to: BR-007)
- **Given** "alice" has just created a group and added no further
  members
- **When** the group's member list is checked
- **Then** it contains exactly one member (alice), and this is a
  valid, non-error state

### Verification scenarios

**SCN-014** (Traces to: NFR-001)
- **Given** 50 concurrent group-creation requests are submitted
  within the same 1-second window
- **When** all 50 are processed
- **Then** the P95 response time across those requests is under 300ms

## Non-Functional Requirements

- **NFR-001**: Group creation completes in under 300ms at P95 under
  normal load (defined as up to 50 concurrent group-creation
  requests, consistent with the load definition used in
  SE-auth-001-NFR-001).

## Traceability Table

| Requirement ID | Description | Business Goal | Scenario(s) | Test(s) |
|---|---|---|---|---|
| SE-group-001-BR-001 | Only an authenticated user can create a group | BG-002 | SCN-001, SCN-005 | TBD |
| SE-group-001-BR-002 | Name non-empty, ≤20 chars at creation | BG-001 | SCN-006, SCN-009, SCN-010 | TBD |
| SE-group-001-BR-003 | Group names may be duplicated | BG-001 | SCN-013 | TBD |
| SE-group-001-BR-004 | Creator auto-added as member | BG-001 | SCN-002 | TBD |
| SE-group-001-BR-005 | Creator designated sole admin at creation | BG-002 | SCN-003 | TBD |
| SE-group-001-BR-006 | Exactly one admin at all times, no reassignment in this spec | BG-002 | None — see Verification scenarios note | TBD |
| SE-group-001-BR-007 | Group may have no members beyond creator/admin | BG-001 | SCN-012 | TBD |
| SE-group-001-BR-008 | Only current admin can edit group name | BG-002 | SCN-004, SCN-007 | TBD |
| SE-group-001-BR-009 | Edited name non-empty, ≤20 chars | BG-001 | SCN-008, SCN-011 | TBD |
| SE-group-001-NFR-001 | Group creation P95 latency < 300ms | BG-002 | SCN-014 | TBD |
| SE-group-001-BR-010 | Name restricted to letters, digits, spaces | BG-001 | SCN-015, SCN-016 | TBD |
| SE-group-001-BR-011 | Accept optional description up to 255 chars | BG-001 | SCN-017 | TBD |
| SE-group-001-BR-012 | Allow admin to edit description | BG-002 | SCN-018 | TBD |
| SE-group-001-BR-013 | Accept optional default_currency (ISO 4217 code) | BG-001 | SCN-019 | TBD |
| SE-group-001-BR-014 | Default to 'USD' if no currency provided | BG-001 | SCN-020 | TBD |

## Open Questions

None

## Changelog

- **1.0.0**: Initial draft — group creation, creator-as-sole-admin,
  and name editing only. Membership management, admin reassignment,
  and group deletion are explicitly out of scope (future specs).
- **1.1.0**: [DELTA] Added optional group description logic. Admin can
  set plain-text description (up to 255 characters) at creation and
  edit it later. Rich-text formatting is out of scope.
- **1.2.0**: [MINOR] Added optional default_currency field (3-letter ISO 4217
  code) at group creation...