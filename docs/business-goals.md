# SplitEasy — Business Goals

Each goal has a stable ID (`BG-###`), a one-line statement, and the
rationale behind it. Specs reference goals by ID only (`BG-001`); this
file is the single source of truth for what each ID means, per
Constitution Section 7.

---

## BG-001: Let a group of people track shared expenses without manual math

**Statement:** Users can record shared expenses within a group and
have the system calculate who owes whom, removing manual tracking
and arithmetic errors.

**Rationale:** This is the core value proposition of SplitEasy. Every
spec touching expense entry, splitting logic, or balance calculation
should trace here.

---

## BG-002: Protect user accounts and group membership from unauthorized access

**Statement:** Only authenticated users can act on the system, and
only members of a group can view or affect that group's expenses and
balances.

**Rationale:** Shared expense data is sensitive (spending habits,
debts between real people). This goal covers authentication, session
handling, and group-membership authorization. Every spec touching
login, tokens, or access control should trace here.

---

## Changelog

- **2026-09-26**: Initial goals (`BG-001`, `BG-002`) added, covering
  `auth` and `group` specs.