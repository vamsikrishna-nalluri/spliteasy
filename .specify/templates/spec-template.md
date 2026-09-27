---
id: SE-[module-name]-001
version: 1.0.0
status: draft
depends_on: []
business_goals: [BG-001]
---

# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[feature/###-feature-name]`

**Created**: [DATE]

**Input**: User description: "$ARGUMENTS"

<!--
  Constitution rules that apply to this whole file:
  - Keep the nine "##" sections below, in this order, with these exact names.
  - Module names are singular and registered in the glossary (e.g. `expense`, not `expenses`).
    Confirm [module-name] is in the glossary, or add it there via PR, before merging this spec.
  - IDs: BR-001, NFR-001, SCN-001 (unique within this spec). Qualified references use a
    hyphen: SE-[module-name]-001-BR-001, SE-[module-name]-001-SCN-004.
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

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently

  Acceptance scenarios are NOT written here. They live in the Scenarios section
  with SCN-### IDs; each story only points to them.
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Scenarios**: SCN-001, SCN-002

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Scenarios**: SCN-003

---

[Add more user stories as needed, each with an assigned priority]

## Scope

### In scope

- [What this spec covers]

### Out of scope

- [What this spec does not cover, with the spec ID that does, if any]

### Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]

## Dependencies

<!-- Other specs by ID (also listed in frontmatter `depends_on`), and existing systems or services. -->

- [SE-[module-name]-001: why this spec depends on it]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]

## Business Rules

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right requirements.

  Money handling: if this feature touches money, state how money is represented
  (as a BR below or in Key Entities). Otherwise write "No monetary values."

  Avoid banned vague words (see constitution Principle 11): fast, performant,
  real-time, instantaneous, scalable, robust, heavy load, user-friendly, intuitive,
  seamless, modern, usually, generally, often, sometimes, as needed, etc., and/or.
  Use concrete, numeric, or exact behavioral wording instead.
-->

- **BR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **BR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **BR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **BR-004**: System MUST [data requirement, e.g., "persist user preferences"]

*Example of marking unclear requirements:*

- **BR-005**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Scenarios

<!--
  Each scenario has an ID (SCN-###), unique in this spec, and MUST declare exactly one
  parent requirement inline: **SCN-001** (Traces to: BR-001). A scenario may not be
  shared between two requirements; a requirement may have multiple scenarios. The
  Traceability Table below must list the same Scenario(s) as these inline tags — the
  inline tag is the source of truth if they ever disagree.

  Scenarios are grouped as Happy path, Failure paths, and Boundary conditions. In an
  `in_review` or `active` spec, each group needs at least one SCN-### or an explicit
  "not applicable" reason. Edge cases from the feature description go under Failure
  paths or Boundary conditions.
-->

### Happy path

**SCN-001** (Traces to: BR-001)
- **Given** [initial state]
- **When** [action]
- **Then** [expected outcome]

**SCN-002** (Traces to: BR-002)
- **Given** [initial state]
- **When** [action]
- **Then** [expected outcome]

### Failure paths

**SCN-003** (Traces to: BR-003)
- **Given** [initial state]
- **When** [error scenario]
- **Then** [expected outcome]

### Boundary conditions

**SCN-004** (Traces to: NFR-001)
- **Given** [initial state]
- **When** [boundary condition]
- **Then** [expected outcome]

## Non-Functional Requirements

<!--
  ACTION REQUIRED: Define measurable requirements.
  Each NFR needs either a numeric threshold with a unit and the measurement condition
  (percentile, time window, or load), or a discrete boolean compliance condition
  (e.g. a named cryptographic standard or regulation). State each threshold once,
  here; scenarios refer to the NFR ID instead of repeating it. Avoid banned vague
  words (see Business Rules note above).
-->

- **NFR-001**: [Measurable metric, e.g., "Account creation completes in under 2 seconds at P95"]
- **NFR-002**: [Measurable metric, e.g., "System handles 1000 concurrent users with P95 response under 500 ms"]

## Traceability Table

<!--
  One row per requirement (BR and NFR). Scenario(s) column must match the inline
  (Traces to: ...) tags in the Scenarios section exactly. Test(s) column: a valid
  TC-[module-name]-### (module must match this spec's own module), or TBD if no
  test exists yet — required coverage is enforced by the CI gate, not this table.
-->

| Requirement ID | Description | Business Goal | Scenario(s) | Test(s) |
|---|---|---|---|---|
| SE-[module-name]-001-BR-001 | [Short description] | BG-001 | SCN-001 | TBD |
| SE-[module-name]-001-NFR-001 | [Short description] | BG-001 | SCN-004 | TBD |

## Open Questions

- None

## Changelog

- **1.0.0**: Initial draft.