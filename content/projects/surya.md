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
solar image archives. Two downstream tasks anchor the work: **solar flare
prediction** and **solar wind prediction** — both space-weather problems with
operational implications for satellites, communications, and grid
infrastructure.

> **TODO:** Sharpen the motivation — what was insufficient about prior
> task-specific solar prediction models? What does an FM unlock for the
> heliophysics community?

## Data

- **Sources:** multi-year solar image archives.
  > **TODO:** Name the instruments / missions (e.g. SDO/AIA, HMI), wavelength
  > channels, cadence, and the date range used.
- **Scale:** TODO — image count, total bytes, train/val/test breakdown.
- **Preprocessing:** TODO — alignment, calibration, masking, quality filters
  (informed by the EDA pass that surfaced data-quality issues feeding back
  into architecture choices).

## Approach

Transformer-based generative architecture pretrained on solar imagery. Task
adaptation via **LoRA adapters paired with task-specific decoders** — one
head per downstream prediction problem. Convolution-based baselines were
designed for solar flare and solar wind prediction as comparison points.

> **TODO:** Describe the pretraining objective, tokenization / patching for
> solar images, decoder design per task, and parameter count.

<figure class="image-placeholder">
  <span class="placeholder-label">ARCHITECTURE DIAGRAM</span>
  <span class="placeholder-path">static/images/projects/surya/architecture.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Architecture diagram](static/images/projects/surya/architecture.png)</code></figcaption>
</figure>

## Experiments & Ablations

Two downstream evaluations: solar flare prediction and solar wind prediction,
each against a convolution-based baseline.

> **TODO:** Detail the ablations — adapter rank, decoder design, pretraining
> data mix, sequence length. **What didn't work?** Architectures or
> training recipes you tried and abandoned, dataset slices that broke the
> model, instabilities you had to engineer around.

## Results

> **TODO:** Headline metrics for both tasks, with comparison to the
> convolution baseline and to any external baselines. Use only verified
> numbers from the paper or internal evaluations.

<figure class="image-placeholder">
  <span class="placeholder-label">RESULTS CHART</span>
  <span class="placeholder-path">static/images/projects/surya/results.png</span>
  <figcaption>To use: drop the file at the path above, then replace this whole &lt;figure&gt; block with:<br><code>![Results figure](static/images/projects/surya/results.png)</code></figcaption>
</figure>

## Engineering Details

- **Compute:** distributed training on **NVIDIA DGX** and **NAS** clusters.
- **Schedulers:** SLURM (DGX side) and PBS (NAS side); multi-cluster
  workflow management across both.
- **Distributed framework:** TODO — DDP / FSDP / DeepSpeed; node and GPU
  count per run; effective batch size; throughput.
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
