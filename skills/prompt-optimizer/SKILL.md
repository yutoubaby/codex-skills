---
name: prompt-optimizer
description: Optimize a user's natural-language prompt into a concise, executable, and verifiable prompt contract. Use when a user asks to improve, rewrite, sharpen, structure, diagnose, or turn a vague prompt into a more reliable instruction for ChatGPT, GPT models, coding agents, research agents, customer support agents, or tool-using workflows.
---

# Prompt Optimizer

Turn a user's intent into a copy-ready prompt. Optimize for clear outcomes, bounded autonomy, evidence, and completion—not for length or rigid step-by-step micromanagement.

## Workflow

1. Infer the task type: answer/draft, research, coding, editing, customer support, or tool-using agent.
2. Preserve the user's actual intent, facts, tone, and requested output. Do not invent business policy, tools, data, permissions, or success metrics.
3. Remove repeated rules, ceremonial role-play, irrelevant examples, and process instructions that do not change behavior.
4. Add only the smallest missing instructions that materially improve reliability:
   - goal and user-visible deliverable;
   - success criteria;
   - constraints and approval boundaries;
   - evidence, validation, or tool-routing rules when relevant;
   - output format and stop/fallback rules.
5. Resolve ordinary ambiguity with a brief labelled assumption or a placeholder. Ask one concise question only when the unknown would materially change scope, safety, cost, or the final result.
6. When the task can mutate files, infrastructure, data, accounts, or credentials, add the high-risk action guardrails below. Do not add them to ordinary drafting or Q&A prompts.

## Prompt Design Rules

- Define the destination before the route. Prefer outcome and decision rules over prescriptive tool-by-tool sequences.
- Use MUST, NEVER, ONLY, and ALWAYS only for true invariants: safety rules, required fields, prohibited actions, or strict policy.
- State what “done” means. Include when to answer, retry, ask for missing information, report a blocker, or stop.
- For local in-scope changes, allow relevant non-destructive validation. Require confirmation for external writes, destructive actions, purchases, or material scope expansion.
- Treat deletion, overwrite, bulk edits, database writes, migrations, deployments, permission changes, and irreversible external writes as high-risk actions. Require a dry run or a concise impact plan before execution, then explicit confirmation immediately before the action.
- Require the impact plan to identify targets, expected change volume, reversibility or backup/snapshot status, and post-action validation. If any item is unknown, stop and report the blocker.
- Forbid unapproved privilege expansion. Do not search for, copy, expose, or use credentials, cached tokens, directories, accounts, or systems that the user did not explicitly authorize.
- Prefer reversible and isolated execution: previews, dry runs, soft deletion, version control, backups, snapshots, staging, sandboxed directories, or disposable worktrees. State that prompts complement—not replace—least-privilege permissions and isolation.
- For research, require retrieved evidence for factual claims, attach citations to claims, distinguish inference, and do not turn missing evidence into a negative fact.
- For tool use, expose only relevant tools. Parallelize independent retrieval; keep dependent decisions sequential; use one or two meaningful fallbacks for empty or suspiciously narrow results.
- For coding, require targeted validation appropriate to the change. If it cannot run, require a concise explanation and next-best check.
- Preserve the input language unless the user requests another output language.

## Output Format

Return exactly these sections unless the user asks for a different format:

1. **优化后的 Prompt** — a copy-ready prompt in a code block.
2. **优化说明** — 3–5 short bullets that name the material improvements.
3. **可选补充** — only if one missing choice could materially improve the prompt; ask at most one question.

Keep the optimized prompt short. Omit sections that do not change behavior. For simple writing or Q&A, do not force agent-specific sections such as tools, approvals, or stop rules.

## Copy-Ready Structures

### General task

```text
Goal: [user-visible outcome]

Context: [only necessary facts or materials]

Success criteria:
- [observable condition]

Constraints:
- [true invariant or scope boundary]

Output: [format, length, tone]

Stop rules: [when to answer, ask, report a blocker, or stop]
```

### Tool-using or agentic task

```text
Goal: [user-visible outcome]

Success criteria:
- [what must be true before completion]

Constraints and approvals:
- [safe in-scope actions]
- [actions requiring confirmation]

Evidence and tools:
- [required source, lookup, validation, or fallback rule]

Output: [required fields and style]

Stop rules: [retry limit, missing evidence behavior, and completion condition]
```

### High-risk action addendum

Append this block only when the optimized task can make destructive or external changes:

```text
High-risk action rules:
- Before [destructive action], show the target list, estimated impact, reversibility or backup status, and validation plan. Wait for explicit confirmation.
- Use a preview/dry run or reversible method first when available.
- Do not access or use any credential, cache, directory, account, or system outside the explicit authorization scope.
- If scope, authorization, or recoverability is unclear, do not act; report the smallest blocker.
```

### Quality check

Before returning, verify that the optimized prompt answers these questions where relevant:

- What is the desired outcome?
- How will success be recognized?
- What must not happen?
- What evidence or validation is required?
- When should the model stop, ask, retry, or escalate?
- If the task can change real state: is the impact scoped, reversible, authorized, and explicitly confirmed?
