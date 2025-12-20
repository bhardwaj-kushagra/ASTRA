# Delivery Roadmap

| Phase | Focus Area | Key Deliverables | Target Duration | Status |
| --- | --- | --- | --- | --- |
| 0 | Discovery & Baselining | Threat taxonomy, data inventory, architecture RFC | 4-6 weeks | Informational |
| 1 | Detection Core MVP | Ingestion backbone, first-gen detectors, evaluation harness | 8-10 weeks | Implemented (prototype) |
| 2 | Attribution & Graph Intelligence | Extend schema with actor_id + source_hash; build simple co-occurrence graph (adjacency list); visualize clusters | 10-12 weeks | Implemented (prototype) |
| 3 | Federation | Define JSON threat exchange format; demonstrate two ASTRA instances exchanging summaries | 12+ weeks | Implemented (prototype) |
| 4 | Red Teaming & Evaluation | Manually craft 10–20 adversarial samples; compare heuristic vs zero-shot failures; track regressions | 8-10 weeks | Implemented (prototype) |
| 5 | Scale-out & Sustainment | Global rollout, SLAs, continuous red-teaming | Ongoing | Future work |

Update milestones after each release review. Pair this roadmap with quarterly OKRs and resource plans.
