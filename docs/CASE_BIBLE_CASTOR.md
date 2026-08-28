# PROJECT CASTOR — canonical case bible
*Fictional scenario, ESM-flavoured. Invented project, invented people. Institutional context is factual; nothing here describes a real ESM project or real ESM staff. Every deliverable built from this bible must carry that disclaimer.*

## 1. The institution (factual background)
The **European Stability Mechanism (ESM)** is the euro area's permanent crisis-resolution
institution, an intergovernmental body established by treaty (not an EU institution),
headquartered in **Luxembourg City (Kirchberg)**. ~230 staff, over 50 nationalities.

- **Authorised capital** ~€709 bn · **paid-in capital** ~€81 bn · **callable** ~€628 bn · **maximum lending capacity** €500 bn.
- Funds itself by **issuing bonds and bills** on the capital markets; paid-in capital guarantees the bonds rather than funding loans directly.
- **Board of Governors** — highest decision-making body; one governor per euro area member state, in practice the finance ministers. Major decisions, including financial assistance, by mutual agreement (unanimity of those voting).
- **Board of Directors** — one director + alternate per member state, persons of high competence in economic and financial matters; day-to-day decision powers delegated by the Board of Governors.
- **Managing Director** — appointed for a five-year term, chairs the Board of Directors, runs day-to-day operations. (Do not name the real post-holder in the story; the story's equivalent is fictional.)
- **Toolkit**: stability support loan · bank recapitalisation programme · precautionary financial assistance (**PCCL** / **ECCL**) · **Primary Market Support Facility (PMSF)** · **Secondary Market Support Facility (SMSF)**.
- The **common backstop to the Single Resolution Fund** would be added by the ESM Treaty reform; ratification is incomplete (Italy has not ratified), so the instrument is a *planned* capability, not a live one. This uncertainty is a real, useful risk driver for the case.
- ESM/EFSF together disbursed close to €300 bn to five programme countries between 2011 and 2018.

## 2. The project
**Project CASTOR — Renewal of the Lending Operations System (LOS)**

**Problem.** LOS was built in the EFSF era and is now 14 years old. Disbursement instructions
are re-keyed by hand between LOS, the treasury system and the payment messaging gateway.
Each new instrument requires bespoke code. Post-disbursement reconciliation takes three days.
Internal Audit raised two findings on segregation of duties and on the completeness of the
audit trail.

**Objective.** Replace LOS with a configurable lending operations platform giving
straight-through processing from loan agreement to disbursement to repayment schedule,
instrument-agnostic product configuration, same-day automated reconciliation, a complete
audit trail, and the ability to onboard the common backstop instrument within weeks of the
Treaty reform entering into force.

**Measurable success criteria (the Business Case's, carried into the Charter)**
| # | Criterion | Baseline | Target |
|---|---|---|---|
| SC1 | Disbursement cycle time, instruction to value date | 5 working days | 1 working day |
| SC2 | Post-disbursement reconciliation | 3 working days | same day |
| SC3 | New instrument onboarding | 9 months | 6 weeks |
| SC4 | Manual re-keying of payment instructions | ~1,400 fields/quarter | 0 |
| SC5 | Open internal-audit findings on LOS | 2 | 0 |

**Budget** €8.4 m · **effort** 3,100 person-days · **duration** 26 months ·
**type of delivery** Mix (in-house core team + outsourced platform implementation).

**Timeline (use these dates verbatim in every artefact)**
| Milestone | Date |
|---|---|
| Project Initiation Request submitted | 12 Jan 2026 |
| Business Case + Project Charter approved | 24 Mar 2026 |
| **RfP gate — Ready for Planning** | 27 Mar 2026 |
| Planning Kick-off Meeting | 09 Apr 2026 |
| Project Handbook + Work Plan baselined | 26 Jun 2026 |
| **RfE gate — Ready for Executing** | 03 Jul 2026 |
| Executing Kick-off Meeting | 10 Jul 2026 |
| Contract award, Levallois Systems | 18 Sep 2026 |
| Release 1 — product configuration engine | 26 Mar 2027 |
| Release 2 — straight-through disbursement | 17 Dec 2027 |
| Parallel run with LOS | 08 Jan – 30 Apr 2028 |
| Transition / go-live | 15 May 2028 |
| **RfC gate — Ready for Closing** | 22 Jun 2028 |
| Project-End Review Meeting | 12 Jul 2028 |
| Administrative closure complete | 28 Jul 2028 |

## 3. Cast — one historical figure per PM² role
These are **mnemonic personas, not historical portrayals**. Each figure holds a modern ESM job and
is written so that the thing they are famous for *is* the thing their PM² role does. That is the whole
point: if you remember that Leonardo never stopped improving the design, you remember that the
Solution Provider is accountable for the deliverables. Nothing any of them says reflects the real
person's views; they died between 1492 and 1993 and never worked in euro-area crisis finance.

| PM² role | Layer | Persona | ESM job title | Why this figure | Voice |
|---|---|---|---|---|---|
| **AGB** — Appropriate Governance Body | Business Governing | **Lorenzo de' Medici** | Deputy Managing Director; chairs the **Corporate Investment Board (CIB)** | The patron. Held the purse for a whole city and always knew what he was *not* funding. | Warm, unhurried, ruthless about trade-offs. Asks what leaves the portfolio. |
| **PSC** — Project Steering Committee | Steering | chaired by Nightingale; members Nightingale, Leonardo, Hopper, you + optional roles | — | — | Formal. Minuted by Gantt. |
| **PO** — Project Owner | Directing | **Florence Nightingale** | Head of Lending Operations Division | Owned the *outcome*, not the building. Counted everything and used the numbers to force change. | Clipped, evidence-first, impatient with anything she cannot measure. |
| **SP** — Solution Provider | Directing | **Leonardo da Vinci** | Head of IT & Digital Division | Accountable for what gets built — and constitutionally unable to stop refining it. | Curious, digressive, protective of his architects. Has to be pulled back to the date. |
| **BM** — Business Manager | Managing | **Grace Hopper** | Senior Loan Operations Officer | Spent her life translating between the business and the machine, and training the people who had to use it. | Direct, practical, funny. "It is easier to ask forgiveness than permission" energy — which PM² will correct. |
| **PM** — Project Manager | Managing | **YOU (the player)** | Project Manager, ESM Project Support Office | — | — |
| **BIG** — Business Implementation Group | Performing | coordinated by Hopper; members from Lending Operations, Finance & Control, Risk, Legal | — | — | Worried about their own workload. |
| **PCT** — Project Core Team | Performing | coordinated by you; **Nikola Tesla** (Lead Solution Architect, seconded from the contractor), **Ada Lovelace** (Business Analyst), dev and test leads, contractor staff | — | — | Technical, literal. |
| **PST** — Project Support Team | Support | **W. Edwards Deming** (PQA), **Henry Gantt** (PSO), **Louis Brandeis** (DPC), **Alan Turing** (LISO), **Johannes Gutenberg** (DMO) | — | — | Procedural. |

**Named individuals in detail**

- **Marie Curie — User Representative (UR)**, Loan Administration Officer. Does the day job the system
  will change. Famous for refusing to accept a measurement she had not verified herself — which is
  exactly what a UR does at deliverable acceptance. Blunt, precise, unbothered by deadlines.
- **Nikola Tesla — Lead Solution Architect**, seconded from **Levallois Systems** into the **Project Core Team**
  (the PM² Guide says the PCT may include contractor staff). Brilliant, difficult, over-designs, and
  **he is the key-person risk R-07 — and on 04 Oct 2027 he resigns**, which is how the story turns a
  *risk* into an *issue*. Speaks in absolutes.
- **Gustave Eiffel — Contractor's Project Manager (CPM)**, Levallois Systems. Delivered a 300-metre tower
  on time and under budget and never let anyone talk to his workers directly. Reports to **you**, and to
  the **PSC** if necessary. Courteous, contractual, immovable.
- **Albert Einstein — Architecture Office (AO)** representative on the PSC. Reframes. Every time the room
  argues about a solution he asks what problem is actually being solved. Slow, mild, disarming.
- **W. Edwards Deming — Project Quality Assurance (PQA)**. Independent of you. Reviews the process, not
  the person. "In God we trust; all others bring data."
- **Ada Lovelace — Business Analyst** on the PCT — a PCT member, *not* a PM² role of its own. Turns
  Hopper's business need into a specification Tesla can build.
- **Henry Gantt — Project Support Office (PSO)**. Schedules, minutes, versions, archives. Invented the bar chart.
- **Alan Turing — Local Information Security Officer (LISO)**. Confidentiality, integrity, availability.
- **Louis Brandeis — Data Protection Coordinator (DPC)**. Co-wrote the article that invented privacy law.
- **Johannes Gutenberg — Document Management Officer (DMO)**. Versions, copies, retention, sanitisation.

**The contractor** is **Levallois Systems**, a fictional platform vendor, awarded the implementation
contract on 18 Sep 2026 under an existing framework contract.

## 4. Running conflicts the story uses (one per phase, so the drama teaches the method)
1. **Initiating** — Florence wants to skip straight to procurement; the Business Case has to justify one recommended option out of three, and the **AGB** wants to know what leaves the portfolio to make room.
2. **Planning** — Leonardo insists the platform is bought, not built; the **Outsourcing Plan** is the artefact where **AGB = Accountable**, which surprises everyone including the PSC.
3. **Planning** — Grace and you collide over **Transition Plan vs Business Implementation Plan**: who owns retraining 40 loan administrators, and which document it lives in.
4. **Executing** — a scope request arrives verbally from a Board of Directors member's cabinet: add SRF-backstop screens now. It must become a **Change Request Form**, an entry in the **Change Log**, a **PSC** decision — not a favour.
5. **Executing** — Levallois's key architect leaves. Risk R-07 materialises: it stops being a **risk** and becomes an **issue**, moving from the **Risk Log** to the **Issue Log**.
6. **Executing** — the parallel run overlaps an EFSF bond rollover; Marie refuses acceptance of the reconciliation report; **Manage Deliverables Acceptance** kicks in with partial acceptance.
7. **Closing** — the benefits will only be measurable in 2029; the **Project-End Report** hands benefit tracking to the permanent organisation, and Florence has to accept that this is normal, not a failure.

## 5. Style rules for anything built from this bible
- Every artefact excerpt is **filled in with CASTOR content**, never `<placeholder>`.
- Figures must stay consistent with §2 across every deliverable.
- PM² terms in their exact English form: *Project Owner (PO)*, *Ready for Planning (RfP)*, *Business Implementation Plan*, *RASCI*.
- Amounts in EUR, dates as `DD Mon YYYY`, person-days as `PD`.
- Never state or imply that a real ESM person or a real ESM project is being described.
