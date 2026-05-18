---
name: "Prithvi WxC — Weather & Climate Foundation Model"
slug: prithvi-wxc
order: 1
blurb: >
  Transformer-based foundation model for weather and climate, developed
  in collaboration with NASA, IBM, Oak Ridge National Laboratory, and
  NVIDIA. Petabyte-scale data pipelines and LoRA-based downstream
  fine-tuning.
tags: [Foundation Models, PyTorch, LoRA, HPC]
links:
  - { label: Paper,       url: "https://arxiv.org/pdf/2409.13598" }
  - { label: HuggingFace, url: "https://huggingface.co/collections/ibm-nasa-geospatial/prithvi-for-weather-and-climate" }
---

## Problem & Motivation

Prithvi WxC is a transformer-based foundation model for weather and climate,
developed in collaboration with NASA, IBM, Oak Ridge National Laboratory, and
NVIDIA. The goal: a single pre-trained backbone that downstream weather and
climate tasks can fine-tune from, instead of training task-specific models
from scratch.

> **TODO:** Explain *why* a foundation model for weather/climate matters —
> the gap in existing approaches, the scientific or operational pain point,
> and what an FM unlocks that task-specific models cannot.

## Data

- **Sources:** TODO — name the reanalysis datasets used (e.g. MERRA-2, ERA5),
  variables, and temporal coverage.
- **Scale:** petabyte-scale reanalysis time-series.
- **Preprocessing:** TODO — chunking strategy, normalization, train/val/test
  splits, handling of missing observations.

## Approach

Transformer backbone pretrained on reanalysis time-series data. Downstream
tasks adapted via LoRA-based parameter-efficient fine-tuning, which keeps
the backbone frozen and trains only low-rank adapter weights — reducing
training cost while maintaining prediction quality.

> **TODO:** Describe the model architecture in more depth — token / patch
> design, masking objective during pretraining, choice of attention
> variants, hidden size / depth, total parameter count.

<figure class="image-placeholder">
  <span class="placeholder-label">ARCHITECTURE DIAGRAM</span>
  <span class="placeholder-path">static/images/projects/prithvi-wxc/architecture.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Architecture diagram](static/images/projects/prithvi-wxc/architecture.png)</code></figcaption>
</figure>

## Experiments & Ablations

> **TODO:** Which downstream tasks did you evaluate (e.g. forecasting,
> downscaling, gap filling)? Which ablations did you run (LoRA rank,
> adapter placement, pretraining objective, data mix)? **What didn't work
> — failed architectures, training instabilities, dataset choices you
> reverted?**

## Results

> **TODO:** Headline metrics versus baselines. Include numbers only when
> they're from the actual paper or a verified internal evaluation — do not
> estimate. Link to the paper for full tables.

<figure class="image-placeholder">
  <span class="placeholder-label">RESULTS CHART</span>
  <span class="placeholder-path">static/images/projects/prithvi-wxc/results.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Headline results](static/images/projects/prithvi-wxc/results.png)</code></figcaption>
</figure>

## Engineering Details

- **Data pipelines:** end-to-end processing of petabyte-scale reanalysis
  time-series across **isolated computing environments** (no internet
  egress on the HPC side).
- **Distributed training:** TODO — which clusters, scheduler, framework
  (DDP / FSDP / DeepSpeed), node and GPU count, throughput.
- **Fine-tuning infra:** TODO — where downstream LoRA fine-tunes run
  (cloud vs. on-prem), turnaround per task.

## Reflections

> **TODO:** What surprised you about training at this scale? What would you
> do differently in the next FM build? What transferable lessons came out
> for the broader ML team?

## Links

- **Paper:** <https://arxiv.org/pdf/2409.13598>
- **HuggingFace:** <https://huggingface.co/collections/ibm-nasa-geospatial/prithvi-for-weather-and-climate>
- **Code:** TODO — add public repo URL if/when available.
- **Demo / notebooks:** TODO.
