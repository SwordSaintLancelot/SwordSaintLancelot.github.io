---
name: "Prithvi WxC — Weather & Climate Foundation Model"
slug: prithvi-wxc
order: 1
blurb: >
  Vision Transformer-based foundation model for weather and climate, developed
  in collaboration with NASA, IBM, Oak Ridge National Laboratory, and
  NVIDIA. Petabyte-scale data pipelines and LoRA-based downstream
  fine-tuning.
tags: [Foundation Models, PyTorch, LoRA, HPC]
links:
  - { label: Paper,       url: "https://arxiv.org/pdf/2409.13598" }
  - { label: HuggingFace, url: "https://huggingface.co/collections/ibm-nasa-geospatial/prithvi-for-weather-and-climate" }
---

## Problem & Motivation

Prithvi WxC is a vision transformer-based (ViT) foundation model for weather and climate,
developed in collaboration with NASA, IBM, Oak Ridge National Laboratory, and
NVIDIA. The goal was  to create a unified pre-trained backbone that can be fine-tuned for
downstream weather and climate tasks, instead of training task-specific models
from scratch.

Numerical weather prediction (NWP) models consume intensive compute to provide weather predictions whereas 
Foundation models for weather and climate create a unified backbone using similar amount
of compute which can be used for multiple downstream cases. For decades, scientist have used NWPs to 
predict weather forecasts. Nowadays comparable results are being achieved using AI methods with the possibility
to use the same models for multiple tasks utilizing a fraction of data that would be used in either NWPs or a task specific model.

## Data

- **Sources:** MERRA-2 reanalysis, 160 atmospheric variables.
- **Scale:** petabyte-scale time series on a 0.5° × 0.625° lat/lon grid at
  3-hour cadence; each sample is shaped 320 × 360 × 576.
- **Splits:** 1980–2019 for pretraining; 2020–2023 reserved for validation
  / downstream evaluation depending on task.

## Approach

Transformer backbone pretrained on MERRA-2 reanalysis time-series. The
final model has **2.3 B parameters** across 25 encoder + 5 decoder blocks,
with internal dim 2560, 16 attention heads, and an MLP multiplier of 4.
Inputs are split into 2×2-pixel patches over 30×32 windows (15×16 tokens),
yielding 51,840 tokens per sample.

Pretraining runs in two phases: masked reconstruction with alternating
local/global masking, followed by autoregressive rollout tuning. A key
design choice was modeling the **deviation from climatology** at each
timestamp rather than predicting raw state or simple state-difference
tendencies — this stabilized training and made zero-lead-time tasks
tractable.

Downstream tasks are adapted via LoRA-based parameter-efficient
fine-tuning, which keeps the backbone frozen and trains only low-rank
adapter weights — reducing training cost while maintaining prediction
quality.

![Architecture diagram](static/images/projects/prithvi-wxc/architecture.png)

## Experiments & Ablations

**Pretraining (two phases):**
- *Phase 1 — masked reconstruction.* 100,000 gradient steps on 64× A100
  (80 GB) GPUs at batch size 1, 50% masking with alternating local/global
  patterns, 5% stochastic depth (drop path).
- *Phase 2 — autoregressive rollout.* 0% masking, Swin-shift added, 1–3
  rollout steps for forecast tuning on 16–48 GPUs depending on rollout
  depth.

**Downstream tasks evaluated:** zero-shot reconstruction (gap filling),
medium-range forecasting, hurricane track forecasting, statistical
downscaling, and gravity-wave flux parameterization.

**What didn't work / had to engineer around:**
- *Tendency prediction.* Predicting raw state differences broke zero
  lead-time tasks → switched to modeling deviation from climatology.
- *Lead-time context tokens.* Specialized transformer layers collapsed
  attention onto these tokens, which conflicted with stochastic depth →
  replaced with learned δt (forecast lead) and δτ (input step) embeddings.
- *3D masking.* Memory blew past 80 GB per GPU; abandoned in favor of the
  2D masking schedule above.
- *Numerical instability on cloud-liquid-water.* Extreme value ranges at
  high pressure levels forced bounded normalization
  (10⁻⁴ ≤ σ ≤ 10⁴, 10⁻⁷ ≤ σ_C ≤ 10⁷).

## Results

- **Zero-shot reconstruction:** recovers atmospheric state from as little
  as **5%** of inputs when remaining samples are spatially dense, and
  **25%** when large contiguous regions are masked out — all without any
  task-specific tuning.
- **Forecasting:** strong at 6–12 h lead times, particularly for surface
  temperature; honest about the falloff — Prithvi WxC drops below
  Pangu-Weather past ~66 h on standard medium-range metrics.
- **Hurricane Ida (Cat 4) track forecasting:** mean track error
  **63.9 km** vs. **201.9 km** for MERRA-2 FourCastNet and **262.3 km**
  for ERA5 FourCastNet; landfall location error **<5 km** vs. **>20 km**
  for the FourCastNet baselines. Consistent outperformance across a
  75-event composite through 5-day lead.
- **Statistical downscaling:** MERRA-2 6× T2m spatial RMSE **0.73 K**
  (vs. 3.22 K nearest-neighbor / 3.08 K bilinear); CORDEX 12× tas RMSE
  **0.44 K** (vs. 1.89 K / 1.47 K). ~4× and ~3× better than the
  interpolation baselines respectively.
- **Gravity-wave flux parameterization:** spatial correlation **0.99**
  for the Andes region and **0.97** for the Southern Ocean.

![Hurricane Downstream Results](static/images/projects/prithvi-wxc/downstream_hurricane.png)

## Engineering Details

- **Data pipelines:** end-to-end processing of petabyte-scale reanalysis
  time-series across **isolated computing environments** (no internet
  egress on the HPC side). Climatology is precomputed from 20 years of
  MERRA-2 with a 61-day rolling window; static fields (elevation, land /
  ocean / ice fractions) are materialized as monthly files for fast
  loading.
- **Distributed training:** FSDP (Fully Sharded Data Parallel) with Flash
  Attention on A100 (80 GB) GPUs. Phase 1 runs on 64 GPUs at batch size 1;
  Phase 2 runs on 16–48 GPUs depending on rollout depth.
- **Mixed precision:** bf16 in transformer blocks, fp32 at input/output
  layers; activation checkpointing enabled throughout.
- **Schedule:** cosine-annealed learning rate from 1e-4 to 1e-5 after a
  linear warmup.
- **Memory envelope:** ~43 GB/GPU at pretraining; supports up to 4
  autoregressive rollout steps on an 80 GB A100 with masking (3 without).

## Reflections

> **TODO:** What surprised you about training at this scale? What would you
> do differently in the next FM build? What transferable lessons came out
> for the broader ML team?

## Links

- **Paper:** <https://arxiv.org/pdf/2409.13598>
- **HuggingFace:** <https://huggingface.co/collections/ibm-nasa-geospatial/prithvi-for-weather-and-climate>
- **Code:** https://github.com/NASA-IMPACT/Prithvi-WxC
