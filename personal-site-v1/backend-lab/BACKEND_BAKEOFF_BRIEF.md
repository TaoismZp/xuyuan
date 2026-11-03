# Backend Capability Bakeoff — Personal Site v1

Status: ACTIVE — capability procurement and representative spikes only. Production backend construction is not authorized until this gate closes.

## Accepted frontend contract
Frontend Delivery Identity: `b82b5bb2496d9b7ccd960f0785e7fde15e86be0a`.

The backend must serve the accepted static frontend; it may not force a frontend/framework rewrite unless a representative test proves a major quality gain that outweighs migration cost.

## Representative owner task
From an iPhone-class authoring surface, the single owner should be able to create or edit a Chinese longform article with:
- title
- optional dek
- slug
- date
- tags
- draft/published state
- Markdown/rich-text body

After publish, the durable source must have version history / rollback, and the static frontend must be able to build the article/archive from that source without changing its visual system.

## Quality variables
1. Owner mobile authoring UX — 25%
2. Fits accepted static frontend without migration — 20%
3. Secure owner auth; no browser token leakage — 15%
4. Draft/edit/unpublish/version/rollback reliability — 15%
5. Operational burden / extra server / payment / maintenance — 10%
6. Markdown + structured-content compatibility — 10%
7. Future expansion to projects/about/media — 5%

## Candidates
- Pages CMS hosted + GitHub-backed content
- Sveltia CMS static admin + GitHub backend
- TinaCMS Git-backed headless CMS
- Payload CMS as full-server comparator
- Existing GitHub Issue + Actions publisher as no-CMS control

## Hard gates
- No solution wins by requiring the accepted frontend to become Next.js/React solely to satisfy the CMS.
- No browser-stored long-lived GitHub PAT is accepted as the default owner experience.
- No solution may hide a required external server/database behind the phrase “static CMS”.
- Auth that requires a one-time GitHub App/OAuth installation is allowed, but it is recorded as a real user-side setup gate.
- A hosted editor is acceptable if the public content remains portable Git/Markdown and the hosted service is not required for readers.
- Auth cannot be faked in CI; where third-party login cannot be exercised, source-level evidence must state the limitation.
