---
name: "US Greenhouse Gas Center"
slug: us-ghg-center
order: 3
blurb: >
  Automated geospatial pipelines (Airflow + STAC + COGs) on AWS,
  supporting a platform presented at the White House and COP28.
tags: [Geospatial, AWS, Airflow, STAC]
links:
  - { label: Project, url: "https://earth.gov/ghgcenter" }
---

## Problem & Motivation

The US Greenhouse Gas Center provides a single, discoverable platform for
greenhouse gas measurements and model outputs across federal agencies.
The data engineering challenge: take heterogeneous geospatial datasets from
multiple producers and make them queryable, cloud-native, and reproducible
without manual handling.

> **TODO:** Add the stakeholder framing — which agencies, what users
> (scientists, policy, public), and what the platform replaced or
> consolidated.

## Data

- **Sources:** TODO — list the contributing datasets / agencies (NASA, NOAA,
  EPA, etc.) and what each provides.
- **Scale:** TODO — number of datasets, total bytes, update cadence.
- **Preprocessing:** automated conversion of source geospatial data to
  **Cloud-Optimized GeoTIFFs (COGs)** so they stream efficiently from
  object storage; cataloging into **STAC**-compliant metadata stores for
  discovery.

## Approach

End-to-end pipeline orchestrated with **Apache Airflow**:

1. Ingest from upstream providers
2. Transform to Cloud-Optimized GeoTIFFs
3. Register into STAC catalog
4. Expose via the platform's API for downstream consumers

> **TODO:** Add a sequence / pipeline diagram showing dataset lifecycle from
> producer → COG → STAC → API.

<figure class="image-placeholder">
  <span class="placeholder-label">PIPELINE DIAGRAM</span>
  <span class="placeholder-path">static/images/projects/us-ghg-center/pipeline.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Pipeline diagram](static/images/projects/us-ghg-center/pipeline.png)</code></figcaption>
</figure>

## Experiments & Ablations

> **TODO:** This section is less applicable for a data-platform project than
> for an ML one — consider replacing with "Design Decisions": which choices
> were considered (e.g. Zarr vs. COG, alternative catalog standards) and
> why STAC + COG won; what limits you ran into; what you'd reconsider.

## Results

The platform was **presented at the White House and at COP28**, making the
GHG data programmatically accessible to scientists, policymakers, and the
public.

> **TODO:** Add quantitative outcomes you can verify — dataset count served,
> API request volume, latency, time-to-publish (provider → live), etc.
> Avoid invented numbers.

<figure class="image-placeholder">
  <span class="placeholder-label">PLATFORM SCREENSHOT</span>
  <span class="placeholder-path">static/images/projects/us-ghg-center/screenshot.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Platform screenshot](static/images/projects/us-ghg-center/screenshot.png)</code></figcaption>
</figure>

## Engineering Details

- **Orchestration:** Apache Airflow DAGs for ingestion + transformation.
- **Compute:** AWS — **Lambda** for event-driven transforms, **API Gateway**
  for the public API surface, **EC2** for backing services.
- **Storage / catalog:** Cloud-Optimized GeoTIFFs on object storage,
  metadata in STAC-compliant catalogs.
- **Monitoring:** TODO — observability stack, alerting, on-call rotation.

## Reflections

> **TODO:** What would you change about the ingestion contract with data
> producers? What scaling pain points appeared as more datasets came
> onboard? What's the most reusable piece of this for other geospatial
> platforms?

## Links

- **Platform:** <https://earth.gov/ghgcenter>
- **Code:** TODO — public GitHub org / repo if available.
- **Talks / press:** TODO — White House and COP28 references.
