---
name: "Prithvi EO 2.0 — Earth Observation Foundation Model"
slug: prithvi-eo
order: 5
blurb: >
  Multi-temporal Vision Transformer foundation model for Earth observation,
  pretrained on NASA Harmonized Landsat-Sentinel (HLS) imagery and
  benchmarked across GEO-Bench, flood / wildfire / landslide mapping,
  crop segmentation, and biomass regression.
tags: [Foundation Models, Earth Observation, ViT, MAE, TerraTorch]
links:
  - { label: Paper,       url: "https://arxiv.org/pdf/2412.02732" }
  - { label: HuggingFace, url: "https://huggingface.co/ibm-nasa-geospatial" }
  - { label: Code,        url: "https://github.com/IBM/terratorch" }
---

## Problem & Motivation

Prithvi EO 2.0 is a geospatial foundation model for Earth observation,
developed in collaboration with NASA, IBM, and the Jülich Supercomputing
Centre. The goal was to address three gaps in existing EO foundation
models: most do not exploit the inherently multi-temporal nature of
satellite data, validation across diverse downstream tasks remains thin,
and adapting state-of-the-art models to new applications still requires
heavy AI expertise. Prithvi EO 2.0 ships alongside the **TerraTorch**
toolkit so that the broader EO community can fine-tune the backbone on
their own tasks without a full ML stack.

## Data

- **Source:** NASA Harmonized Landsat and Sentinel-2 (HLS) archive,
  2014–2023, six spectral bands (Blue, Green, Red, NIR, SWIR1, SWIR2).
- **Scale:** **4.2 M** global multi-temporal samples, each with **4
  timestamps** at 256×256 pixels at 30-m resolution. Sampled from
  **3,028 training tiles + 163 validation tiles** out of ~18,000 HLS
  tiles globally, prioritizing land-use / land-cover diversity and
  ecoregion coverage.
- **Cadence:** 1–6 month intervals between consecutive timestamps in a
  sample.
- **Quality filtering:** samples with >1% missing values or >20% cloud
  cover excluded.

## Approach

Prithvi EO 2.0 is a **masked autoencoder (MAE)** with an asymmetric
encoder-decoder, extended to handle spatio-temporal satellite data:

- 2D patch and positional embeddings replaced with **3D versions**; a 3D
  convolutional layer divides the input into non-overlapping cubes with
  temporal stride `t = 1`.
- Separate 1D sin/cos positional encodings for time, height, and width.
- **Metadata encoding:** latitude, longitude, year, and day-of-year are
  encoded with sin/cos features and added to tokens via a learned
  weighted sum (the "TL" — temporal/location — variant).
- **Pretraining objective:** MSE between masked and predicted tokens,
  with random patch masking. Only unmasked tokens flow through the
  encoder.

Released sizes: **300 M parameters (ViT-L)** and **600 M parameters
(ViT-H)**, each with and without TL embeddings. Downstream tasks adapt
the backbone with task-specific decoders (UPerNet, U-Net, FCN) and
LoRA-based parameter-efficient fine-tuning for select tasks.

![Architecture diagram](static/images/projects/prithvi-eo/fig10_prithvi_eo2.png)

## Experiments & Ablations

**Pretraining:** 400 epochs with random crops to 4×224×224 and horizontal
flips for augmentation; metadata drop probability 0.1; global batch size
**3,840**; AdamW with cosine schedule, peak LR 5e-4 after a 40-epoch
linear warmup from 1e-6; weight decay 0.05.

**Benchmarking protocol (GEO-Bench):** 12 datasets — 6 classification and
6 segmentation — across spatial resolutions of 0.1–15 m. For fair
comparison, all models use uniform 224×224 resizing and the same spectral
bands. Hyperparameters tuned via Bayesian optimization (10 trials);
results averaged over N=10 seeds with different random initializations.

**Ablations:**
- *Temporal / location embeddings.* The TL-equipped variants
  (Prithvi-EO-2.0-600M-TL and the 300M-TL) gave the best combined
  performance across the benchmark suite — confirming that geographic
  and seasonal context, when injected explicitly, helps over a vanilla
  ViT.
- *Model size.* Larger backbones consistently beat smaller ones; the
  600 M model is the top performer overall.
- *Pretraining data scale.* Comparing a 100 M model pretrained on the
  global dataset vs. a US-only subset produced a **+3% lift on the
  overall GEO-Bench score** — useful evidence that global coverage
  matters beyond just total token count.
- *Low-data regime.* Downstream fine-tuning was evaluated at 1% / 5% /
  10% data fractions to characterize the foundation model's behavior
  when labeled data is scarce.

## Results

Headline downstream numbers (verified from the paper):

- **GEO-Bench overall:** **~8% improvement** over Prithvi-EO-1.0 across
  the 12-task suite; Prithvi-EO-2.0-600M and 600M-TL are among the top
  performers on both classification and segmentation averages.
- **Flood mapping (Sen1Floods11):** water IoU **83.1%** (600M-TL) vs.
  79.6% for Prithvi-EO-1.0.
- **Wildfire scar mapping:** burn-scar IoU **83.2%** vs. 76.8% previously.
- **Landslide detection (Landslide4Sense, full data):** mIoU **71.3%**,
  F1 **60.7%** with the 300M model.
- **Few-shot landslide (50 images):** mIoU **67.0%**, F1 **49.7%** with
  the 600M model — robust transfer in the scarce-label regime.
- **US crop segmentation:** mIoU **50.7%**, mean accuracy 68.8% (600M).
- **Europe land cover (Sen4Map, full data):** F1 **76.1%** (600M).
- **PASTIS crop segmentation:** mIoU **53.4%** at 100% data; **37.4%**
  at 10% data — graceful degradation under low-data conditions.
- **Above-ground biomass regression:** RMSE **33.40 Mg/ha** with 12
  Sentinel-2 timestamps.


## Engineering Details

- **Compute:** trained on the **JUWELS Booster** supercomputer at the
  Jülich Supercomputing Centre.
  - 300 M models: **80× A100 (40 GB)** GPUs, ~**21,000 GPU-hours**,
    400 epochs.
  - 600 M models: **240× A100 (40 GB)** GPUs, ~**58,000 GPU-hours**,
    400 epochs.
- **Effective batch size:** 3,840 across all configurations.
- **Framework:** PyTorch Lightning + TorchGeo; pretraining and
  fine-tuning workflows packaged into the **TerraTorch** toolkit, with
  TerraTorch-iterate driving hyperparameter search through Optuna.
- **Decoders:** UPerNet for transformer backbones, U-Net for ResNet
  baselines, FCN where appropriate per task.
- **Fine-tuning constraint:** all downstream experiments are designed to
  run on a **single GPU** — typical configuration is encoder LR 5e-4 /
  decoder LR 5e-5, batch size 48 (300M) or 16 (600M), 50–100 epochs with
  early stopping (patience 10–20).

<!-- ## Reflections

> **TODO:** What did you take away from validating across 20+ downstream
> tasks rather than a handful? How did the TerraTorch integration change
> the way external teams adopt the model? What would you change about
> the pretraining-data sampling strategy in a v3 build? -->

## Links

- **Paper:** <https://arxiv.org/pdf/2412.02732>
- **HuggingFace:** <https://huggingface.co/ibm-nasa-geospatial>
- **TerraTorch:** <https://github.com/IBM/terratorch>
