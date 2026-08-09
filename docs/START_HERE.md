# START HERE — Session Operating Procedure

This file is intentionally boring. Follow it before **every** learning session.

## A. Starting a session

### If continuing in the same ChatGPT chat

1. Open this repository.
2. Read `docs/PROJECT_STATE.md`.
3. Run:
   ```bash
   git status
   git log -1 --oneline
   ```
4. In ChatGPT type:
   > Continue AI Incident Copilot from PROJECT_STATE. First tell me today's goal and the exact first task only. Keep following MASTER_PLAN and do not skip Definition of Done items.

### If starting a fresh ChatGPT chat

Prefer a fresh chat when the previous chat has become long or when starting a new major phase.

1. Create the new chat **inside the same ChatGPT Project**.
2. Attach/provide the latest:
   - `docs/MASTER_PLAN.md`
   - `docs/PROJECT_STATE.md`
   - `docs/DECISIONS.md` only when architecture decisions are relevant.
3. Type exactly:
   > Continue my 14-day AI Engineer capstone, Production AI Incident & Knowledge Copilot. Treat MASTER_PLAN.md as the syllabus and PROJECT_STATE.md as the exact source of current progress. Do not repeat completed work. First summarize in 5 bullets where I am, today's goal, and give me only the next task.

## B. During a session

The teaching loop is:

1. Problem being solved
2. Minimal theory
3. Why this technology
4. Alternatives
5. Our tradeoff
6. Implement
7. Run
8. Break/test
9. Measure
10. Production implications
11. Interview questions
12. Update project state

Ask questions whenever something is unclear.

A question does **not** change project state unless work is actually completed.

If a side topic would take more than ~15 minutes and is not required for today's objective, record it in `docs/TOPICS_TO_REVISIT.md` and continue.

## C. When you believe the session is done

Tell ChatGPT exactly:

> Done with today's session. Check MASTER_PLAN Definition of Done against what we actually implemented. Do not mark anything complete just because we discussed it. Give me exact replacement/update text for PROJECT_STATE.md, DECISIONS.md, EXPERIMENTS.md, LEARNING_NOTES.md, INTERVIEW_QA.md and TOPICS_TO_REVISIT.md only where each file actually needs changes. Then give me the git commands for the checkpoint commit.

Do not leave the session until:

- [ ] code runs
- [ ] required tests/experiment ran
- [ ] you can explain the main tradeoff
- [ ] interview questions were attempted
- [ ] `PROJECT_STATE.md` is updated
- [ ] relevant learning/decision/experiment files are updated
- [ ] `git status` is reviewed
- [ ] checkpoint is committed

## D. End-of-session Git ritual

```bash
git status
git diff
git add .
git commit -m "day-XX: <short outcome>"
git status
```

If a GitHub remote is configured:

```bash
git push
```

## E. Rule for completion

A technology is NOT “learned” because it was installed or mentioned.

For major topics, completion requires as applicable:

- THEORY — can explain what problem it solves
- IMPLEMENTED — wrote or integrated working code
- TESTED — verified success and at least one failure/edge case
- MEASURED — captured a useful metric where applicable
- TRADEOFF — can compare at least one alternative
- INTERVIEW — answered project-specific questions without reading notes

`MASTER_PLAN.md` is the final authority.
