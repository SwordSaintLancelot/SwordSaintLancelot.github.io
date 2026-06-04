---
name: "Sanoma Media Finland — Recommendation Platform Modernization"
slug: sanoma-recommender
order: 5
thumbnail: static/images/projects/sanoma-recommender/sanome_recommender.png
blurb: >
  Production ALS collaborative-filtering recommender integrated with
  content delivery across Sanoma's digital media platforms.
tags: [Recommender Systems, Python, Production ML]
---

## Context

I worked at Sanoma on the recommendation system powering two of its
streaming platforms — **ruutu.fi** (video on-demand) and **supla.fi**
(podcasts and radio). The recommender was already in production by the
time I joined: an **ALS (Alternating Least Squares) collaborative
filtering** model, deployed through Sanoma's in-house **Unified
Recommendation Framework** and integrated with the content-delivery path
so items were scored at request time.

My role was to contribute to that system's modernization and
experimentation surface — not to build it from scratch. This page
describes the parts I actually touched.

<figure class="project-figure">
  <img src="static/images/projects/sanoma-recommender/system-overview.png"
       alt="Sanoma streaming recommendation flow: events from ruutu.fi and supla.fi feed into the Unified Recommendation Framework (feature pipeline → ALS → request-time scoring), which delivers ranked items to algorithmic rows in the streaming UI.">
</figure>


## Approach

The system was built on **ALS collaborative filtering** over implicit
engagement signals — watches, listens, dwell time, repeat visits. The
matrix factorization yields per-user and per-item latent embeddings; at
request time, candidate items are scored as the dot product of a user
vector with item vectors, and the top-ranked items populate
personalized rows in the streaming UI.

<figure class="project-figure">
  <img src="static/images/projects/sanoma-recommender/als-concept.png"
       alt="ALS conceptual diagram: a sparse user-item interaction matrix is approximated as the product of a tall user-embedding matrix U and a wide item-embedding matrix V transpose, both with k latent factors.">
</figure>

ALS specifically suits implicit-feedback recommendation at this scale —
it parallelizes cleanly, handles sparsity well, and the model is
inexpensive to retrain on a regular cadence. The framework layered
business and editorial rules on top of the raw scores; the model didn't
decide everything that went into a carousel.

## What I worked on

### Translating the Scala codebase to Python

The recommender was written in **Scala**. I started porting parts of the
codebase to Python. The motivation was iteration cost — the rest of the
data-science team was working in Python (notebooks, pandas, scikit-learn,
plotting), and the JVM build-and-deploy loop was adding friction to model
experimentation. Moving the data-prep and modeling layers into Python
brought them closer to where the experimentation was actually happening.

This was part of a broader pipeline-modernization effort at Sanoma:
legacy Scala data pipelines were being progressively refactored into
Python across the data team.

### ALS experimentation for supla.fi

Alongside the translation work, I built proof-of-concept experiments
applying ALS to **supla.fi** specifically. supla's content dynamics
differ from ruutu's — different catalog size, different sparsity
profile, different repeat-engagement patterns (a podcast listener and a
video viewer don't behave the same way). The parameters and
implicit-feedback weighting that worked well on ruutu didn't transfer
directly, so the POCs explored how to tune ALS for supla's signal mix.

### Carousel UX feedback

Recommendations only matter once they reach a user, and the way scores
are surfaced shapes whether they get acted on. I worked with the product
side on the streaming UI's recommendation carousels — observing how
rows were laid out, providing feedback on ordering and visibility, and
on the interaction between editorially-curated rows and algorithmic
rows. This wasn't a model change; it was making sure the right scores
reached the user in a form they could act on.

<figure class="project-figure">
  <img src="static/images/projects/sanoma-recommender/carousels.png"
       alt="Mockup of the streaming UI showing how algorithmic and editorial rows coexist: an editor's-pick hero banner at the top, an algorithmic Recommended for you row in the middle, and editorially-managed Continue watching and Trending now rows.">
</figure>

## Engineering notes

- **Production integration** went through the **Sanoma Unified
  Recommendation Framework**, which scored items at request time and
  served them through the content-delivery path.
- **Pipeline modernization** — legacy Scala data pipelines were being
  refactored into Python to accelerate iteration. My translation work
  sat inside that broader trajectory.
- **Two platforms, one framework** — ruutu.fi and supla.fi shared the
  framework but needed different tuning. The supla POCs were the first
  step toward treating them as distinct recommendation domains rather
  than one configuration.