---
name: "Sanoma Unified Recommendation Framework"
slug: sanoma-recommender
order: 4
blurb: >
  Production ALS collaborative-filtering recommender integrated with
  content delivery across Sanoma's digital media platforms.
tags: [Recommender Systems, Python, Production ML]
---

## Problem & Motivation

Sanoma's digital media platforms publish editorial content across multiple
properties. Editorial reach and engagement depend on surfacing the right
story to the right reader at the right time — a personalization problem
that scales with the platform and changes with the news cycle.

> **TODO:** Sharpen the business framing — what KPI was the recommender
> moving (click-through, session depth, return rate, subscription
> conversion)? What was the editorial vs. algorithmic tension and how was
> it managed?

## Data

- **Sources:** user engagement events across Sanoma's digital media
  platforms (clicks, reads, dwell, repeat visits).
- **Scale:** TODO — daily active users, event volume per day, catalog size
  (articles indexed), feature pipeline cadence.
- **Preprocessing:** TODO — session reconstruction, negative sampling
  strategy, cold-start handling for new articles and new users.

## Approach

**ALS (Alternating Least Squares) collaborative filtering**, deployed as
part of the **Sanoma Unified Recommendation Framework** and integrated
directly with content delivery so recommendations are served inline with
editorial content.

> **TODO:** Why ALS over alternatives (neural CF, two-tower, content-based)?
> How were implicit vs. explicit signals weighted? How were editorial
> rules / business constraints (e.g. mandatory inclusions, freshness
> windows) layered on top of the model output?

<figure class="image-placeholder">
  <span class="placeholder-label">SYSTEM DIAGRAM</span>
  <span class="placeholder-path">static/images/projects/sanoma-recommender/architecture.png</span>
  <figcaption>TODO: Replace this block with a system diagram showing model training, feature pipeline, and content-delivery integration.</figcaption>
</figure>

## Experiments & Ablations

> **TODO:** What variants did you test before settling on ALS? What were
> the offline-vs-online evaluation gaps? **What didn't work** — failed
> features, models that beat ALS offline but lost online, A/B tests that
> regressed engagement?

## Results

> **TODO:** Headline business impact — click-through lift, engagement
> deltas, retention impact. Use only numbers you can cite from internal
> evaluations or public Sanoma materials. Do not estimate.

<figure class="image-placeholder">
  <span class="placeholder-label">A/B TEST RESULT CHART</span>
  <span class="placeholder-path">static/images/projects/sanoma-recommender/results.png</span>
  <figcaption>TODO: Replace this block with the headline A/B result, or remove if not shareable.</figcaption>
</figure>

## Engineering Details

- **Production integration:** the model serves recommendations through the
  Sanoma Unified Recommendation Framework, wired into the content-delivery
  path so impressions are scored at request time.
- **Training cadence:** TODO — retrain frequency, training infra, time
  budget per refresh.
- **Serving:** TODO — latency target, request volume, fallback when the
  recommender is unavailable.
- **Pipelines:** part of broader pipeline modernization at Sanoma —
  legacy Scala data pipelines were refactored into Python to accelerate
  data-science iteration.

## Reflections

> **TODO:** What does ALS do well in production that flashier models
> often don't? What would you change about the offline-online evaluation
> coupling in retrospect? How did collaboration with editorial teams
> shape the system?

## Links

- **Code:** TODO — public reference if any (most likely internal-only).
- **Talks / writeups:** TODO — Sanoma engineering blog, conference talks.
