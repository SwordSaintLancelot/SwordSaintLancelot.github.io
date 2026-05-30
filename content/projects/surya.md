---
name: "Surya — Heliophysics Foundation Model"
slug: surya
order: 2
blurb: >
  Co-developed a generative architecture trained on multi-year solar
  image archives for solar flare and solar wind prediction. Distributed
  training on NVIDIA DGX / NAS clusters via SLURM and PBS.
tags: [Foundation Models, Computer Vision, Distributed Training]
links:
  - { label: Paper,       url: "https://arxiv.org/pdf/2508.14112" }
  - { label: HuggingFace, url: "https://huggingface.co/nasa-ibm-ai4science/Surya-1.0" }
---

## Problem & Motivation

Surya is a generative foundation model for heliophysics, trained on multi-year
solar image archives, developed in collaboration with NASA, IBM, NVIDIA, CSPAR and many other prestigious
institutes across USA. The goal was to create a model that would be able to predict various solar activities,
like solar flares, solar winds and EUV epectra for advancement in space weather, along with helping the
scientific community utilize machine learning to advance space weather.

<!-- > **TODO:** Sharpen the motivation — what was insufficient about prior
> task-specific solar prediction models? What does an FM unlock for the
> heliophysics community? -->

## Data

- **Sources:** FITS files from stanford Joint Science Operations Center containing files with 8 frequencies
of Atmospheric Imaging Assembly(AIA) channels, and 5 for Helioseismic and Magnetic Imager(HMI)
  <!-- > **TODO:** Name the instruments / missions (e.g. SDO/AIA, HMI), wavelength
  > channels, cadence, and the date range used. -->
- **Scale:** ~257 TB across 13 channels (8 AIA + 5 HMI) at the native 4096×4096
  resolution (0.6″/pixel), spanning May 13, 2010 – Dec 31, 2024. Standardized
  to a 12-minute cadence after discussions with the science domain experts;
  train/val/test split was aligned with solar cycles, with temporal buffer
  days excluded around the test window to prevent leakage.
<!-- TODO — image count, total bytes, train/val/test breakdown. -->
- **Preprocessing:** Multiple pre-preocessing steps using helio physics python slibraries like sunpy were
performed in order to align the data, apply corrections and transform them into netCDF files from raw FITS format
<!-- TODO — alignment, calibration, masking, quality filters
(informed by the EDA pass that surfaced data-quality issues feeding back
into architecture choices). -->

## Approach

Surya employed a spatio-temporal transformer-based generative architecture including spectral gating and
long short attention mehcanism pretrained on SDO dataset. The primary pre-training objective was to predict
the next `n` timestamps. The model was further optimized on the autoregressive rollouts.
Zero shot evaluations were generated to showcase the model's ability to forecast solar dynamics and flare events.
Other downstream tasks, like solar wind forecasting, active region segmentation were implemented using
LOw-RAnk adptation. Most impressive point to note about Surya is that the model uses the full resolution `4096*4096`
image resolution for training.

<!-- > **TODO:** Describe the pretraining objective, tokenization / patching for
> solar images, decoder design per task, and parameter count. -->

<figure class="image-placeholder">
  <span class="placeholder-label">ARCHITECTURE DIAGRAM</span>
  <span class="placeholder-path">static/images/projects/surya/architecture.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Architecture diagram](static/images/projects/surya/architecture.png)</code></figcaption>
</figure>

## Experiments & Ablations

**Pretraining (two phases):**
- *Phase 1 — time advancement.* 160,000 gradient steps on 128× A100 GPUs,
  batch size 1 per GPU (effective 128), cosine-annealed learning rate from
  1e-4 to 1e-5.
- *Phase 2 — autoregressive rollout tuning.* Progressive 2 → 5 step rollouts
  on 64 GPUs at reduced learning rates, with gradient checkpointing after
  every layer to fit memory.

**Ablations:**
- *Spectral gating vs. extra attention.* Swapping the two spectral gating
  blocks for additional long-short attention blocks yielded the same training
  loss but cost ~6% more GPU memory, so spectral gating stayed.
- *Rollout tuning vs. Phase 1 only.* At a 12-hour horizon, rollout tuning
  improved forecast quality by 10.9% / 12.3% / 14.9% / 17.8% across the
  evaluated channels.

**What didn't work / had to engineer around:**
- Extending rollout training to a 24-hour horizon was blocked by data-loading
  throughput, not model capacity — the bottleneck was I/O on the 4096×4096
  inputs, which is what motivated the lz4-compressed netCDF pipeline below.
- Magnetic field channels are noise-dominated at native scale; raw inputs
  destabilized training until we adopted the sign-log normalization
  (Engineering Details).

## Results

Evaluated against convolutional baselines (AlexNet, ResNet50, UNet) and,
where applicable, the operational reference model.

- **Active region segmentation:** IoU **0.768** / Dice **0.853** vs. UNet
  0.688 / 0.801 — with only **4.1 M** trainable parameters against UNet's
  9.2 M.
- **Solar flare forecasting (24-hour window, M/X-class threshold):**
  TSS **0.436**, HSS **0.522**, F1 **0.561**. AlexNet TSS 0.358;
  ResNet50 TSS 0.018.
- **Solar wind forecasting (4-day lead time):** RMSE **75.92 km/s**,
  MAE 58.06 km/s. AlexNet RMSE 118.6; ResNet50 RMSE 93.76; published
  WindNet variants 84–86 km/s.
- **EUV spectra (1343 bands):** MAPE **1.48%**, matching the operational
  FISM2 model at 1.5% — and beating AlexNet / ResNet50 on MSE and MAE.
- **Zero-shot forecasting:** outperforms a persistence baseline (MSE 0.594)
  and a learned-flow baseline (MSE 0.338) before any task-specific tuning.

<figure class="image-placeholder">
  <span class="placeholder-label">RESULTS CHART</span>
  <span class="placeholder-path">static/images/projects/surya/results.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Results figure](static/images/projects/surya/results.png)</code></figcaption>
</figure>

## Engineering Details

- **Compute:** distributed training on **NVIDIA DGX** and **NAS** clusters —
  Phase 1 used 128× A100 GPUs; rollout tuning ran on 64 GPUs.
- **Schedulers:** SLURM (DGX side) and PBS (NAS side); multi-cluster
  workflow management across both.
- **Model:** 366 M parameters — 2 spectral gating blocks + 8 long-short
  attention blocks + 1 decoder; internal dim D = 1280; 16×16 patches →
  65,536 tokens; Fourier position embeddings.
- **Mixed precision:** fp32 at input/output layers, bf16 in transformer
  blocks, with an explicit fp32 cast around FFT ops to keep spectral gating
  numerically stable.
- **Training stability:** gradient clipping at 0.1; gradient checkpointing
  after every layer during rollout tuning.
- **Normalization:** sign-log transform with scale factor 1e-2, applied
  per channel — needed for the noise-dominated magnetic field inputs.
- **Data pipeline:** raw FITS → netCDF with lz4 compression (~630 MB/file,
  ~30% smaller than uncompressed); preprocessing covers exposure correction,
  roll-angle alignment, and bilinear interpolation to a common scale, using
  `sunpy` and related helio-physics libraries.
- **Validation:** results validated alongside the heliophysics science team.

## Reflections

> **TODO:** What did training across two different HPC environments teach
> you? How did the EDA findings reshape the modeling plan? What would you
> change about the pretraining-vs-fine-tuning split in hindsight?

## Links

- **Paper:** <https://arxiv.org/pdf/2508.14112>
- **HuggingFace model:** <https://huggingface.co/nasa-ibm-ai4science/Surya-1.0>
- **Code:** TODO.
- **Demo / notebooks:** TODO.
