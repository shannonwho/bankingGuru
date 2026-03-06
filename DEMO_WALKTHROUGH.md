# Claude Code Demo Walkthrough (~15 min)

## Story
A new engineer just onboarded at FinTechCo. Day one, they're assigned a ticket: let customers dispute fraudulent transactions. This walkthrough follows them from "I've never seen this codebase" to "PR is up for review" — entirely inside Claude Code.

---

## Pre-Demo Setup

1. `git checkout main` — clean starting point, no dispute feature exists
2. Start dev servers (`uvicorn` + `npm run dev`) in background terminals
3. Open `http://localhost:5173` — show the app with accounts and transactions, but no disputes
4. Have Linear open with [DIS-17](https://linear.app/dispute-payment-demo/issue/DIS-17/dispute-submission-flow-for-fraudulent-transactions) in Backlog
5. To reset between demo runs:
   - Move DIS-17 back to Backlog in Linear
   - Restore DIS-17's description to just the user requirements (strip any implementation plan)
   - `git checkout main && git branch -D feature/dis-17-dispute-submission-flow`
   - Recreate: `git checkout -b feature/dis-17-dispute-submission-flow`

---

## Act 1: Onboarding — "What is this codebase?" (2 min)

**Prompt:**
> I just joined the team. Help me understand this codebase — what does it do, how is it organized, and what should I know before I start building?

**Value:** A new engineer gets fully oriented in 30 seconds instead of spending half a day reading docs and asking teammates. Claude reads the project's conventions file (`CLAUDE.md`) and source code, then gives a clear mental model of the architecture.

---

## Act 2: Ticket Review — "What am I building?" (1 min)

**Prompt:**
> Look up my assigned ticket DIS-17 in Linear and tell me what I need to build.

**Value:** Engineer stays in their terminal — no context-switching to a browser. Claude pulls the ticket directly from Linear via MCP integration and summarizes the requirements.

> **DIS-17 should contain user-level requirements like:**
> - Customers can dispute a transaction they believe is fraudulent
> - Disputes must be filed within 120 days of the transaction
> - Customers can see the status of their disputes (submitted, under review, resolved, rejected)
> - Each transaction can only be disputed once

---

## Act 3: Plan Mode — "How should I build it?" (3 min)

This is the most important act to highlight. Claude Code has two distinct modes, and best practice is to **plan before you build**.

### 3.1 — Enter plan mode

**Action:** Press `Shift+Tab` to toggle into **plan mode** (or type `/plan`). The input indicator changes to show you're in planning mode.

**Explain to audience:** "Plan mode tells Claude to think and propose — but not touch any files. No code is written, no commands are run. This is how you stay in control."

### 3.2 — Ask Claude to plan

**Prompt (in plan mode):**
> Based on DIS-17 and the existing codebase patterns, create a technical implementation plan for this feature.

**What Claude does (read-only — no edits):**
- Reads existing models, schemas, routers, and frontend components to understand patterns
- Produces a structured technical plan:
  - **Database**: Dispute model fields, relationships, status enum
  - **API**: endpoints (POST submit, GET list, GET detail), validation rules, status codes
  - **Frontend**: components (DisputeForm, DisputeList), pages, API calls, types, sidebar nav
  - **Business rules**: 120-day window, one dispute per transaction, state machine
  - **Tests**: what scenarios need coverage

**Value:** This is the "senior engineer in the room" moment. The plan references actual files and conventions in the codebase — not a generic answer. The engineer reviews it before any code exists.

### 3.3 — Write the plan back to Linear

**Prompt (still in plan mode):**
> This plan looks good. Update DIS-17 in Linear with this technical implementation plan under the description, so it's documented for the team.

**What Claude does:**
- Uses Linear MCP to update DIS-17's description with the technical plan
- Preserves the original user requirements at the top
- Adds an **Implementation Plan** section with the backend, frontend, and test breakdown
- Moves DIS-17 from Backlog → In Progress

**Value:** The ticket is now the single source of truth — user requirements AND technical plan live together. Any teammate or reviewer can see exactly what's being built and why. This is how production teams work: plan is documented before code is written.

**Action:** Show Linear — the ticket now has both the original requirements and the technical plan.

---

## Act 4: Execution Mode — "Go build it." (4 min)

### 4.1 — Switch to execution mode

**Action:** Press `Shift+Tab` to toggle back to **execution mode**. The input indicator changes back.

**Explain to audience:** "Now we're in execution mode. Claude can read files, write code, and run commands. The plan is approved — now we execute."

### 4.2 — Build the full feature

**Prompt (in execution mode):**
> Execute the plan — build the full dispute feature end-to-end.

**What Claude does:**
- Creates the database model, API endpoints, and Pydantic schemas
- Adds frontend pages, components, API calls, types, and navigation
- Follows every convention in the codebase automatically (because it read them during planning)
- All files are created in the right places, matching existing patterns

### 4.3 — Show the working feature

**Action:** Refresh `localhost:5173`. Walk through the working feature live:
- Submit a dispute on a transaction
- See it appear in the disputes list
- Try to dispute an old transaction — blocked by the 120-day rule
- Try to dispute the same transaction twice — blocked

**Key message:** One prompt. Full-stack feature. Working in the browser. The plan was the blueprint — execution followed it precisely.

---

## Act 5: Quality — "Make it production-ready." (3 min)

### 5.1 — Lint & type check

**Prompt:**
> /lint-fix

Then:
> /type-fix

**Value:** Custom slash commands encode the team's quality standards. These aren't generic linters — they're the team's specific workflow, codified as reusable skills in `.claude/commands/`.

### 5.2 — Generate and run tests

**Prompt:**
> /test

**Value:** Claude generates tests that match the team's testing philosophy — happy paths, error cases, boundary conditions (119 days OK, 121 days rejected), state machine transitions. Runs them and iterates until all pass.

---

## Act 6: Ship — "Commit and open a PR." (2 min)

**Prompt:**
> /commit

Then:
> /pr

**Value:** The full shipping workflow in two commands:
- `/commit` — reviews all changes, writes a meaningful commit message, stages only the right files
- `/pr` — pushes the branch, creates a structured PR on GitHub, moves the Linear ticket to "In Review", updates the ticket with an implementation summary, and creates follow-up issues for any deferred work

**Action:** Show the PR on GitHub. Show the Linear ticket updated to "In Review" with the implementation summary added below the plan.

---

## Summary

### Plan Mode vs Execution Mode
| | Plan Mode | Execution Mode |
|---|---|---|
| **What Claude does** | Reads code, proposes approach | Writes code, runs commands |
| **Files modified** | None | Yes |
| **When to use** | Before building, during design | After plan is approved |
| **Toggle** | `Shift+Tab` or `/plan` | `Shift+Tab` again |
| **Best practice** | Always plan first for non-trivial features | Execute against an approved plan |

### What we just saw
| What | Without Claude Code | With Claude Code |
|---|---|---|
| Onboard to a new codebase | Half a day | 30 seconds |
| Understand and plan a feature | Senior pairing session | 1 prompt in plan mode |
| Document the plan in the ticket | Manual write-up | Automatic Linear update |
| Build a full-stack feature | 1-2 days | 4 minutes |
| Lint, type-check, test | Manual runs + fixes | 3 slash commands |
| Commit + PR + ticket sync | 20 min across 3 tools | 2 slash commands |

### Why it works
- **`CLAUDE.md`** — Project conventions written once, followed every time by every engineer and by Claude.
- **Plan mode** — Think before you build. The engineer reviews the approach before any code is written.
- **Custom skills (`/commands`)** — The team's SDLC workflow is codified, not memorized.
- **MCP integrations** — Linear and GitHub stay in sync without leaving the terminal.

### One takeaway
Claude Code doesn't replace engineers — it removes the friction between knowing what to build and having it built. The engineer's judgment drives every step: they review the plan, approve the approach, and validate the result. Claude handles the execution.
