# spliteasy Constitution

Project: **spliteasy** — An expense-sharing service.

## 1. Every requirement has an ID and a scenario

Requirements are typed and numbered within their spec: business rules (`BR-001`) and non-functional requirements (`NFR-001`). Outside their own spec, they are fully qualified by the spec ID (e.g., `SE-expense-001-BR-001`). 

* Every requirement must have at least one GIVEN-WHEN-THEN scenario.
* Scenarios have an ID in the form `SCN-001`, unique within its spec.
* Every scenario traces to exactly one requirement (`BR-###` or `NFR-###`). This parentage must be explicitly declared at the start of the scenario definition (e.g., `**SCN-001** (Traces to: BR-001)`). 
* A scenario may not be shared between two requirements, but a requirement may have multiple scenarios.

*Test:* For specs in strict states (`in_review`, `active`), every requirement (`BR-###` or `NFR-###`) has at least one linked `SCN-###`. Every `SCN-###` present in the document must explicitly declare exactly one parent requirement ID that exists in the same spec.

## 2. Specs are semantically versioned

Specs use semantic versioning (semver): **major** for breaking changes, **minor** for additive changes, and **patch** for clarifications.

*Test:* Every version bump has a Changelog entry declaring its change type (breaking, additive, clarification). The version segment that changed (major, minor, patch) must match the declared type. Whether a change genuinely qualifies as breaking is a judgment made by the author and confirmed in spec review, not something CI enforces.

## 3. Money handling is explicit

Money handling must be stated explicitly in every spec.

*Test:* Every spec that touches monetary values states how money is represented.

## 4. Every spec has frontmatter and traces to a business goal

Every spec has an ID in the form `SE-<module-name>-001` and begins with YAML frontmatter containing the following fields: 
* `id`
* `version`
* `status` (must be `draft`, `in_review`, `active`, `deprecated`, `superseded`, `archived`, or `abandoned`)
* `depends_on`
* `business_goals` (must contain at least one business goal ID in the form `BG-001`)

*Test:* Parsing any spec's frontmatter yields all required fields, `id` matches `SE-<module-name>-###`, `status` matches one of the seven allowed states, and `business_goals` lists at least one `BG-###`.

## 5. Tests trace to scenarios

Every test has an ID in the form `TC-<module-name>-###` and references the spec scenario it verifies. This is done using trace tags in the comments directly above the test definition. The comment character used depends on the programming language, but the tags must explicitly contain `tc:` and `spec:`.

**Examples by language:**

**Python:**
```python
# tc: TC-expense-001
# spec: SE-expense-001-SCN-004
def test_expense_split_equal():
    ...
```

**TypeScript / JavaScript:**
```typescript
// tc: TC-expense-001
// spec: SE-expense-001-SCN-004
test('should split the expense equally', () => {
    ...
});
```

**Go:**
```go
// tc: TC-expense-001
// spec: SE-expense-001-SCN-004
func TestExpenseSplitEqual(t *testing.T) {
    ...
}
```

*Test:* Every test definition carries a comment line containing `tc:` matching `TC-<module-name>-###` and a comment line containing `spec:` matching `SE-<module-name>-001-SCN-###`. That scenario ID must resolve to an existing scenario in the referenced spec. CI tools must be configured to parse the appropriate comment syntax for the repository's language.

## 6. Technical Stack constraints

The stack is Python 3.11+, FastAPI, pytest, and SQLite. 

*(Note: SQLite is designated for MVP/local-first architecture; write-concurrency limitations must be managed or scaled to standard SQL dialects as the project evolves).*

*Test:* The project runs on Python 3.11+, and its dependencies for the web layer, test runner, and database include FastAPI, pytest, and SQLite respectively.

## 7. Specs follow a standard structure

Every spec contains these sections, in exact order: 
1. User Story
2. Scope (in scope and out of scope)
3. Dependencies
4. Business Rules
5. Scenarios
6. Non-Functional Requirements
7. Traceability Table
8. Open Questions
9. Changelog

A section with nothing to say states "None". Every version bump adds a Changelog entry. Unresolved decisions are recorded under Open Questions rather than assumed silently. Business goals are defined in `docs/business-goals.md`, and every `BG-###` used in a spec must exist there.

**Lifecycle and Strictness:**
* Specs with `in_review` or `active` status must have a scenario for every requirement. (Test coverage thresholds are enforced by the CI gate on the codebase, not by the constitution).
* Specs with `draft` or `abandoned` status are exempt from strict requirement-to-scenario mapping, allowing for iterative design or incomplete archival.
* Specs with `deprecated`, `superseded`, or `archived` status are considered frozen; historical mapping must remain valid, but they are exempt from retroactive CI mapping requirements if the constitution rules evolve.

*Test:* All nine headings are present in order, and the latest version in the frontmatter has a matching Changelog entry. `in_review` and `active` specs must pass full scenario mapping checks.

## 8. Scenarios cover happy, failure, and boundary cases

Scenarios are grouped under **Happy path**, **Failure paths**, and **Boundary conditions**. Each group has at least one scenario, or explicitly states why it does not apply.

*Test:* For specs in strict states (`in_review`, `active`), the Scenarios section has all three groups present, each with a `SCN-###` or an explicit "not applicable" reason. (Specs in `draft` or `abandoned` status may simply state "None" under the Scenarios heading. Specs in frozen states—`deprecated`, `superseded`, `archived`—are exempt from structural re-validation).

## 9. Non-functional requirements are measurable and stated once

Every NFR must be strictly verifiable. It must have either a numeric threshold and the condition it is measured under (percentile, time window, or load), OR a discrete boolean compliance condition (e.g., cryptographic standard, regulatory compliance). A threshold/condition is written only in its NFR; scenarios refer to the NFR ID instead of restating it.

*Test:* Every `NFR-###` contains a verifiable condition (numeric unit + measurement condition, or strict boolean check), and no NFR text is repeated in a scenario.

## 10. Every requirement appears in the traceability table

Each spec has a traceability table with one row per requirement, providing the requirement ID, description, business goal, scenario(s), and test(s). 

**Source of Truth:** The scenario's inline `(Traces to: ...)` declaration (defined in Principle 1) is the authoritative source of truth for parentage. The traceability table is a summary projection; if the table and the inline tags disagree, the inline tag takes precedence and the CI build must fail until the table is corrected.

*(Note: To manage versioning smoothly, expected `TC-###` identifiers should be defined in the traceability table during the spec design phase before code is written. If a test is not yet implemented, the test ID column must state `TBD`. If test IDs must be added or updated after a spec is marked `active`, this change is strictly classified as a **patch** version bump, as it enhances traceability without altering the underlying business rules.)*

*Test:* Every `BR-###` and `NFR-###` has a row with at least one `BG-###`, one `SCN-###`, and either one valid `TC-<current-module-name>-###` (which must exactly match the current spec's module) or the literal string `TBD`. The scenarios listed in the table must perfectly match the authoritative `(Traces to: ...)` tags defined in the Scenarios section.

## 11. Requirements avoid ambiguous language

Business Rules and Non-Functional Requirements must be atomic, unambiguous, and testable. To ensure verifiability, specs must strictly avoid subjective or unquantifiable terms. 

**Banned Vague Words:**
* *Performance:* "fast", "performant", "real-time", "instantaneous" (use specific time/latency thresholds).
* *Scalability:* "scalable", "robust", "heavy load" (use specific concurrent user/request metrics).
* *UX/Design:* "user-friendly", "intuitive", "seamless", "modern" (use exact behavioral steps).
* *Ambiguous Modifiers:* "usually", "generally", "often", "sometimes", "as needed", "etc.", "and/or".

*Test:* Requirements (`BR-###` and `NFR-###`) must not contain the banned vague words. Automated linting during the CI process should flag these words as errors, requiring the author to replace them with concrete logic or numeric thresholds.

## 12. Glossary

### Current Module Names
*(Note: This is not a closed set. New modules must be registered in this glossary via PR before their specs are merged).*
* `auth`
* `group`
* `expense`

### Document ID Format
* **Format:** `SE-group-001`
* **SE:** spliteasy (the project name)
* **group:** module name
* **001:** sequence number per module
 
### Reference Rule
All qualified IDs use a hyphen (`SE-<module>-001-<TYPE>-<NNN>`). The type prefix (`BR`, `NFR`, `SCN`, `TC`, `BG`) disambiguates what kind of reference it is.