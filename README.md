# Tidal Prediction: uptide vs utide

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## Overview

This repository provides a direct comparison of tidal water-level predictions produced by two widely used Python libraries — **utide** and **uptide** — using harmonic constituent data from a macro-tidal site in Patagonia, Argentina.

The goal is to quantify and explain the differences between the two libraries when given identical amplitude and phase inputs, and to highlight the practical implications of their different internal conventions for users who need to switch between them or validate one against the other.

## Background

### Tidal Harmonic Analysis

Tidal prediction via harmonic analysis expresses sea-surface elevation as a superposition of sinusoidal constituents, each characterised by a well-known astronomical frequency, an amplitude, and a phase. Given a set of harmonic constants (amplitude *H* and Greenwich phase lag *g*) the predicted water level at time *t* is:

```
η(t) = Σ f_i · H_i · cos(σ_i · t + V_i + u_i - g_i)
```

where `σ_i` is the angular frequency, `V_i` is the astronomical argument, and `f_i`, `u_i` are nodal correction factors that account for the 18.6-year lunar nodal cycle.

### Study Site

Constituent data were extracted from a macro-tidal location in **Patagonia, Argentina** (approximate latitude −50°). The site is dominated by the M2 semi-diurnal constituent (amplitude ≈ 2.86 m), making it a demanding test case for tidal prediction software. Predictions span **January 2020** at a 10-minute interval.
