# PROJECT POLLUX — canonical case bible (PM²-Agile)
*Fictional scenario, ESM-flavoured. Invented project, invented people. The institutional context is
factual; nothing here describes a real ESM project or real ESM staff. Every deliverable built from this
bible must carry that disclaimer.*

**Castor and Pollux are the twins of Gemini.** POLLUX is the sequel to Project CASTOR — same
institution, same governance, several of the same people, but delivered the **PM²-Agile** way.
The reader has already played CASTOR, so the sequel's job is to show what changes and what does not.

## 1. The institution (factual)
The **European Stability Mechanism (ESM)** is the euro area's permanent crisis-resolution institution,
established by treaty, headquartered in **Luxembourg (Kirchberg)**, ~230 staff from over 50 nationalities.
Authorised capital ~**€709 bn**, paid-in ~**€81 bn**, callable ~**€628 bn**, maximum lending capacity
**€500 bn**. It funds itself by issuing bonds and bills. Governed by the **Board of Governors**
(euro area finance ministers), the **Board of Directors**, and a **Managing Director**.
Do not name real post-holders.

## 2. The project
**Project POLLUX — Member-State Exposure Reporting Portal**

**Problem.** After CASTOR went live in May 2028, the lending platform holds clean, current data — but
nobody outside Lending Operations can see it. Exposure reporting to the Board of Directors, to Risk,
and to national authorities is still assembled by hand: eleven spreadsheets, four analysts, five working
days per quarter-end, and a version-control problem that Internal Audit has now named twice. Worse,
**nobody agrees what the report should contain.** Risk wants stress scenarios. The Board wants one page.
Finance wants reconciliation to the accounts. Each quarter the requirements change.

**Why PM²-Agile and not PM² core.** This is the point of the case and it must be argued, not assumed.
CASTOR had a known destination — replace a system that already did a defined job. POLLUX does not:
the requirement genuinely is not knowable in advance, the users cannot describe what they want until
they see it, and the value arrives incrementally. **PM²-Agile does not replace PM².** The governance
layers, the Business Case, the Project Charter, the phases and the gates all stay. What changes is how
the Executing phase is run.

**Objective.** One portal where any authorised user sees current, reconciled exposure by member state,
instrument and maturity, with the numbers traceable back to the lending platform, and where a new report
view can be delivered in one iteration instead of one quarter.

**Measurable success criteria (Business Case → Project Charter)**
| # | Criterion | Baseline | Target |
|---|---|---|---|
| SC1 | Quarter-end exposure pack assembly | 5 working days, 4 analysts | 1 day, 1 analyst |
| SC2 | Time to deliver a new report view | ~1 quarter | 1 iteration (2 weeks) |
| SC3 | Manually maintained spreadsheets in the reporting chain | 11 | 0 |
| SC4 | Figures traceable to the lending platform without manual mapping | ~40% | 100% |
| SC5 | Open internal-audit findings on reporting version control | 2 | 0 |

**Budget** €4.6 m · **effort** 1,850 person-days · **duration** 18 months ·
**delivery** in-house agile team with two seconded contractor members.

**Cadence.** Iterations of **two weeks**. Releases roughly **quarterly**, four in total.
Daily Stand-up every morning. Iteration Review and Retrospective on the last day of each iteration.
Release Planning at least once per iteration.

**Timeline (use these dates verbatim)**
| Milestone | Date |
|---|---|
| Project Initiation Request | 04 Sep 2028 |
| Business Case + Project Charter approved | 12 Oct 2028 |
| **RfP gate — Ready for Planning** | 16 Oct 2028 |
| Development Handbook + Development Work Plan baselined | 27 Nov 2028 |
| **RfE gate — Ready for Executing** | 04 Dec 2028 |
| Iteration 1 begins | 08 Jan 2029 |
| Release 1 — exposure by member state, read-only | 29 Mar 2029 |
| Release 2 — instrument and maturity views, reconciliation panel | 28 Jun 2029 |
| Release 3 — scenario overlay, national-authority access | 27 Sep 2029 |
| Release 4 — self-service report builder | 20 Dec 2029 |
| Transition into service | 31 Jan 2030 |
| **RfC gate — Ready for Closing** | 14 Feb 2030 |
| Administrative closure complete | 20 Mar 2030 |

## 3. Cast — the PM²-Agile roles
Same mnemonic principle as CASTOR: each historical figure's famous trait *is* their role.
**Mnemonic personas, not portrayals.**

| Role | Person | Job | Why this figure |
|---|---|---|---|
| **PM** — Project Manager | **YOU** | Project Manager, ESM Project Support Office | You keep the PM² role. PM²-Agile does not delete it. |
| **BM** — Business Manager | **Grace Hopper** | Senior Loan Operations Officer | Same as CASTOR. Still the business's daily voice. |
| **PrOw** — Product Owner | **Marie Curie** | Head of Reporting, Lending Operations | She refused to sign for 998 of 1,000 loans in CASTOR. Now she owns the **Work Items List** and decides what gets built first. Nobody argues with her acceptance criteria. |
| **TeCo** — Team Coordinator | **Ada Lovelace** | Team Coordinator | The Business Analyst from CASTOR, promoted. She turns intention into specification, and now facilitates the team that builds it. |
| **ArOw** — Architecture Owner | **Albert Einstein** | Architecture Owner, seconded from Enterprise Architecture | He reframes. Every enabler story starts with him asking what problem is actually being solved. |
| **ATeM** — Agile Team Member | **Hedy Lamarr** | Developer | Consistently underestimated, and consistently right about the hard technical problem. |
| **ATeM** | **Charles Babbage** | Data engineer | He builds the engine. Also famously never finished one, which is a live risk. |
| **ATeM** | **Gustave Eiffel** | Seconded lead, Levallois Systems | On time, under budget, and contractually precise about what "done" means. |
| **PO** — Project Owner | **Florence Nightingale** | Head of Lending Operations Division | Unchanged. Still accountable for the benefits. |
| **SP** — Solution Provider | **Leonardo da Vinci** | Head of IT & Digital Division | Unchanged. Still accountable for the deliverables. |
| **AGB** | **Lorenzo de' Medici** | Deputy Managing Director, chairs the Corporate Investment Board | Unchanged. Still asks what leaves the portfolio. |
| **PQA** | **W. Edwards Deming** | Quality & Methods | Unchanged — and delighted, because retrospectives are his life's work. |
| **PSO** | **Henry Gantt** | Project Support Office | Unchanged, and quietly appalled that nobody wants a Gantt chart. |
| **DPC** | **Louis Brandeis** | Data Protection Coordinator | National-authority access raises real questions. |
| **LISO** | **Alan Turing** | Local Information Security Officer | Same. |
| **DMO** | **Johannes Gutenberg** | Document Management Officer | Same. |

**Nikola Tesla does not appear.** He resigned in October 2027, during CASTOR. He is referred to once.

## 4. Running conflicts (one per act, so the drama teaches the method)
1. **Why agile at all** — Medici asks why he should fund something that cannot tell him what it will
   deliver. The answer is not "agile is faster"; it is that the requirement is genuinely unknown and
   PM²-Agile still gives him a Business Case, a Charter and gates.
2. **The Development Work Plan is a plan** — Gantt is told the project is agile and assumes there is no
   schedule. There is: **Work Items List + Release Plan + Iteration Plan**, three levels of detail.
3. **PrOw versus BM** — Curie prioritises the Work Items List; Hopper represents the Project Owner.
   When they disagree about what goes into Release 2, the guide has an answer about who decides.
4. **The Daily Stand-up becomes a status meeting** — the PM starts attending and asking for updates.
   The guide is explicit that this is not what it is for.
5. **Architecture up front versus emergent** — Einstein wants three iterations of enabler work before
   any business story ships. Curie wants business value in Release 1. **Enabler stories** are the answer.
6. **The Definition of Done is not the acceptance criteria** — a story passes its acceptance criteria in
   the Iteration Review but is not Done, because the team's Definition of Done includes accessibility
   and a data-protection check that nobody ran.
7. **Review versus Retrospective** — after a bad iteration the team wants to discuss what went wrong
   during the Review, in front of stakeholders. That is the Retrospective's job, and mixing them costs
   the team its honesty.
8. **Closing an agile project** — the PM² Closing phase does not disappear. Lessons Learned exist
   alongside eighteen months of retrospectives, and someone has to explain why both.

## 5. Style rules
- Every artefact excerpt is **filled in with POLLUX content**, never `<placeholder>`.
- Figures stay consistent with §2 across every deliverable.
- Exact PM²-Agile terms: *Team Coordinator (TeCo)*, *Product Owner (PrOw)*, *Architecture Owner (ArOw)*,
  *Agile Team Member (ATeM)*, *Work Items List (WIL)*, *Development Work Plan*, *Definition of Done*.
- Amounts in EUR, dates as `DD Mon YYYY`, person-days as `PD`.
- Never state or imply that a real ESM person or a real ESM project is being described.
