# QianCraft product record

## Product

QianCraft Creative Intelligence Workbench is an evidence-backed operating tool for turning Guizhou local-culture research and bounded market observations into traceable cultural-creative product directions. It is a working instrument, not a marketing homepage or an autonomous answer generator.

## Primary users and jobs

- Cultural researchers inspect records, relationships, citations and rights boundaries.
- Product strategists compare platform evidence, adjust weights and select opportunities without overwriting source facts.
- Designers turn a selected opportunity into an editable brief, concept set, concept poster and factory quote/sample brief.
- Project reviewers audit where a decision came from, what remains uncertain and which downstream nodes are stale.

## Core outcome

A user can move through Culture → Market → Strategy → Design → Delivery, intervene at every stage, inspect every node on a dedicated page, and leave with an editable, cited concept package that stops before production release, factory ordering, commercial artwork approval or manufacturing/compliance readiness.

## Current operating proof

- 22 verified Guizhou cultural records and 32 cultural, ethics, legal and collection references; discovered material stays in a separate human-review queue and never enters the formal graph automatically.
- A searchable culture constellation connects records, categories and source references. Desktop users can select, pan, wheel-zoom and operate it from the keyboard; compact touch layouts preserve page scrolling until the user explicitly enters constellation-control mode, then support one-finger pan and two-finger zoom.
- A persistent collection control surface exposes schedule, heartbeat, last attempt/success, partial failure, authorization blockers, candidate review and event history. A polling or heartbeat failure invalidates the previous online state instead of leaving stale success visible.
- 378 clearly time-bounded historical platform samples across Xiaohongshu, Douyin, Bilibili and Weibo. Live market refresh is currently `blocked` because `MEDIACRAWLER_LIVE_ENABLED=false` and none of the four platform authorization sessions is connected; the historical evidence is not relabeled as a live update.
- Eight scored opportunities, nine node instances, ten relationships and three comparable concept directions.
- A seven-stage Human Decision Studio, editable node detail pages, workspace persistence, citations, deep links and honest live/cache/stale/warning/error states.
- A working Design Agent handoff through `DesignPackage`, sample/quotation brief and 1800 × 2400 concept poster.
- A repeatable desktop/mobile UI gate across the workbench and all nine node routes: Python 57 passed, frontend unit tests 5 passed, and Playwright 35 passed / 1 intentionally skipped, alongside typecheck, lint, production build, Ruff, lockfile and artifact-contract checks.
- The collection scheduler can keep working only while a single Tool API/container instance, persistent runtime volume, restart policy, network and required platform authorization remain available. It is not a distributed queue. Local 0.9.1 has not been deployed; the protected online instance remains 0.8.0.

## Experience direction

Tonal Focus Review:

- Calm functional color blocks replace both the earlier dark decorative treatment and the later pure-white monochrome treatment. Warm mineral frames the app, mist blue identifies global commands, muted sage groups tools and evidence, fog blue defines the canvas, and soft clay distinguishes the Inspector.
- A 60px desktop command bar and 72px tool rail frame a dominant node canvas. Evidence, assets and history use a contextual 210px lower drawer; the 330px Inspector overlaps from the right only when it helps the selected task.
- System/SF-like sans typography, fine neutral rules, compact semantic radii and one restrained overlay shadow make the surface feel precise without turning it into a marketing homepage.
- Large product surfaces are not pure white. Color remains low-saturation and functional: it communicates region, selection, focus or status, never ornament. The interface uses no gradients, glass, glow, ethnic decoration or saturated ambient effects.
- Original product, evidence and concept imagery may retain source color. Interface status never relies on color alone; every state also has text, iconography or shape.
- The selected node keeps its geometry and advances through a deep desaturated blue keyline, a light-blue selected surface and bound Inspector/evidence context rather than expansion or decorative effects.
- The canvas behaves as a direct-manipulation work surface: drag empty space with the primary pointer or one finger to pan, Shift-drag to box-select, wheel/pinch to zoom, and drag a node without moving the viewport.
- The culture relationship view is the one deliberate black-canvas exception inside the otherwise white tool. It renders an operational constellation, not a decorative hero: search, category filter, record selection, evidence inspection and view controls remain visible.
- On compact touch layouts the constellation defaults to `pan-y pinch-zoom` so the page remains scrollable. Only the explicit “操作星图” mode takes over one-finger pan and two-finger zoom, and “完成” returns control to the page.
- Collection surfaces separate verified knowledge, pending candidates, historical snapshots and current runtime status. Market evidence and its date window appear before the expandable live-collection controls.
- Every draggable evidence record also exposes a visible “add to canvas” control, so pointer dragging is never the only way to create a canvas node.
- At 760px and below, the header keeps a compact current-phase selector and a 44px deep-blue Run action; controls stay at least 44px, and peripheral panels become reversible overlays.
- The Human Decision Studio keeps deep-blue Save as the sole primary action, groups secondary actions by content width and preserves the complete evidence-to-decision chain on desktop and mobile.
- The Culture constellation overlay, Workspace dialog and Human Decision dialog move focus inside, keep keyboard focus contained, close with Escape and return focus to the invoking control; canvas announcements and movement instructions are localized in Chinese.
- Reduced-motion, increased-contrast and Windows forced-colors preferences retain usable status, focus and selection semantics instead of erasing feedback.

## Non-negotiable boundaries

- Preserve citations, evidence type, time boundary, rights status and machine-versus-human decisions.
- Do not describe historical cached platform data as current live trends.
- Do not promote a discovered URL into verified cultural knowledge without field-level evidence and human review.
- Do not describe the scheduler as continuously producing live market material while the live switch or four platform authorizations are blocked; 7×24 operation is conditional on the single-instance runtime, persistent volume, restart policy, network and authorization.
- Do not use `reference_only` collection pixels in generated or commercial artwork.
- Do not conceal missing image providers, failed calls or stale downstream work.
- Do not expose API keys, crawler cookies or site credentials in the client, repository, logs or documentation.
- Do not claim mass-production, DFM, compliance, community authorization or factory-order readiness from the current concept package.

## Success criteria

The workbench should feel like a restrained professional creative tool: the current task is obvious, important evidence stays one action away, every node can be inspected and operated independently, and complexity appears progressively instead of competing for attention all at once. The culture constellation must remain explorable without trapping compact-page scrolling; collection status must remain honest when a source degrades, authorization blocks or the control plane disconnects. Material UI changes must pass the local quality workflow in `docs/frontend_quality_workflow.md`; an automated pass is evidence, not a claim of complete accessibility certification.
