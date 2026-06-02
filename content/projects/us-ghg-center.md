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

The US Greenhouse Gas Center is a multi-agency collaboration — **NASA**
(lead implementing agency), **NOAA**, the **EPA**, and **NIST** — providing
a single, discoverable platform for greenhouse gas measurements, emissions
inventories, and model outputs that previously lived in separate
agency-specific portals. It serves scientists, policymakers, and the
public, with a focus on three areas: (1) estimates of GHG emissions from
human activities, (2) naturally occurring sources and sinks on land and in
the ocean, and (3) identification and quantification of large methane
emission events from aircraft and space-based observations.

The data engineering challenge: take heterogeneous geospatial datasets
contributed by four agencies and make them queryable, cloud-native, and
reproducible without manual handling.

## Data

- **Contributing agencies:**
  - **NASA** — satellite observations of GHGs, data systems, stakeholder engagement
  - **EPA** — anthropogenic GHG emissions inventories
  - **NOAA** — global reference network (ground + aircraft measurements), WMO calibration standards
  - **NIST** — measurement science, urban emissions (test beds)
- **Representative datasets:** GRA²PES (monthly GHG and air-pollutant
  emissions by economic sector, CONUS), Vulcan fossil-fuel CO₂, OCO-3
  satellite CO₂, EMIT methane plume detections, and the urban test beds —
  Indianapolis Flux Experiment (INFLUX), Los Angeles Megacity (LAM), and
  Northeast Corridor (NEC).
- **Preprocessing:** automated conversion of source geospatial data to
  **Cloud-Optimized GeoTIFFs (COGs)** so they stream efficiently from
  object storage; cataloging into **STAC**-compliant metadata stores for
  discovery via the public STAC API.

## Approach

The platform is built on NASA's **VEDA** (Visualization, Exploration, and
Data Analysis) framework, with three user-facing surfaces:

- **Dashboard** — discovery, interactive stories, and visualization
- **Data Services** — STAC catalog + tiling/raster APIs for programmatic access
- **Analytics Hub** — a JupyterHub environment (hosted by 2i2c) where users
  run analyses next to the data in the cloud

End-to-end pipeline orchestrated with **Apache Airflow** (via the shared
`veda-data-airflow` codebase):

1. Ingest from upstream providers
2. Transform to Cloud-Optimized GeoTIFFs
3. Register into STAC catalog
4. Expose via the platform's API for downstream consumers

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

The platform was **unveiled at COP28 in December 2023** by the NASA
Administrator and EPA Administrator, alongside the White House's national
Greenhouse Gas Monitoring Strategy. The launch made curated GHG datasets
from four federal agencies programmatically accessible — via STAC API,
raster tiling, and a hosted JupyterHub — to scientists, policymakers, and
the public, with all datasets, algorithms, and supporting code released
open-source.

<figure class="image-placeholder">
  <span class="placeholder-label">PLATFORM SCREENSHOT</span>
  <span class="placeholder-path">static/images/projects/us-ghg-center/screenshot.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Platform screenshot](static/images/projects/us-ghg-center/screenshot.png)</code></figcaption>
</figure>

## Engineering Details

- **Orchestration:** Apache Airflow DAGs (Amazon MWAA) for ingestion +
  transformation; infrastructure deployed via Terraform modules.
- **Compute:** AWS — **Lambda** for event-driven transforms, **API Gateway**
  for the public API surface, **EC2** for backing services.
- **Storage / catalog:** Cloud-Optimized GeoTIFFs on S3, metadata in a
  STAC-compliant catalog exposed at `earth.gov/ghgcenter/api/stac`.
- **Analytics:** JupyterHub (operated by 2i2c) sitting next to the data so
  users compute against COGs without local downloads.
- **Open-source posture:** all ingest code, configs, and Jupyter notebooks
  live under the [US-GHG-Center](https://github.com/US-GHG-Center) org;
  data products themselves are released open.

<!-- ## Reflections

> **TODO:** What would you change about the ingestion contract with data
> producers? What scaling pain points appeared as more datasets came
> onboard? What's the most reusable piece of this for other geospatial
> platforms? -->

## Links

- **Platform:** <https://earth.gov/ghgcenter>
- **STAC API:** <https://earth.gov/ghgcenter/api/stac/docs>
- **Code:** <https://github.com/US-GHG-Center> (ingest pipelines via
  [`veda-data-airflow`](https://github.com/NASA-IMPACT/veda-data-airflow);
  notebooks in [`ghgc-docs`](https://github.com/US-GHG-Center/ghgc-docs))
- **Launch (COP28):** [NASA news release, Dec 2023](https://www.nasa.gov/news-release/nasa-partners-launch-us-greenhouse-gas-center-to-share-climate-data/)
- **Architecture writeup:** [Development Seed — An Open Information Platform on Greenhouse Gases](https://developmentseed.org/blog/2023-12-14-ghg-center)
