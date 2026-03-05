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

## Libraries

### utide

[utide](https://github.com/wesleybowman/UTide) is a Python port of the MATLAB UTide toolbox (Codiga, 2011). It provides a full harmonic analysis and reconstruction workflow with built-in support for nodal corrections, Greenwich phase conventions, and confidence-interval estimation. It expects time as **matplotlib datenums** and phases as **Greenwich phase lags in degrees**.

### uptide

[uptide](https://github.com/stephankramer/uptide) is a lightweight Python library designed for straightforward tidal prediction in ocean modelling workflows. It expects elapsed time in **seconds from a user-defined reference epoch** and phases in **radians**, interpreted as local phases at *t = 0*, without applying nodal corrections.

### Key Differences

| Feature | utide | uptide |
|---|---|---|
| Time input | Matplotlib datenums | Elapsed seconds from reference epoch |
| Phase convention | Greenwich phase lag (degrees) | Local phase at *t = 0* (radians) |
| Nodal corrections | Yes (`f`, `u`, `V` factors) | No |
| Latitude required | Yes (for nodal corrections) | No |
| Mean & trend | Supported | Not supported |
| Typical use case | Harmonic analysis & reconstruction | Ocean model boundary forcing |

Because of these differences, predictions from the two libraries given the same amplitude and phase inputs are **not expected to be identical**. The residual is physically meaningful and reflects the nodal correction terms applied by utide.

---

### Study Site

Constituent data were extracted from a macro-tidal location in **Patagonia, Argentina** (approximate latitude −50°). The site is dominated by the M2 semi-diurnal constituent (amplitude ≈ 2.86 m), making it a demanding test case for tidal prediction software. Predictions span **January 2020** at a 10-minute interval.

<!--

## Repository Structure

```
.
├── uptide_vs_utide.py              # Main comparison script
├── comparison_full_constituents.png  # Figure: all 14 constituents
├── comparison_m2s2_only.png          # Figure: M2 + S2 only
└── README.md
```
-->

## Requirements

| Package | Tested version | Purpose |
|---|---|---|
| Python | ≥ 3.8 | Runtime |
| numpy | ≥ 1.21 | Array operations |
| pandas | ≥ 1.3 | Constituent data filtering |
| matplotlib | ≥ 3.4 | Plotting and datenum conversion |
| utide | ≥ 0.3 | Tidal reconstruction with nodal corrections |
| uptide | ≥ 1.3 | Lightweight tidal prediction |

## Installation

Clone the repository and install the dependencies:

```bash
git clone git@github.com:pappas-k/Tidal-Prediction-Uptide-vs-Utide.git
cd Tidal-Prediction-Uptide-vs-Utide
pip install numpy pandas matplotlib utide uptide
```

## Usage

Run the main script directly:

```bash
python uptide_vs_utide.py
```

The script will:

1. Build a utide-compatible coefficient structure from the hard-coded Patagonia constituent data.
2. Reconstruct the tidal signal for January 2020 at 10-minute intervals using both **utide** and **uptide**.
3. Compute and plot the residual (UTide − uptide) for two scenarios:
   - All 14 tidal constituents.
   - M2 + S2 constituents only.
4. Save both figures as PNG files and print summary statistics (RMSE and maximum absolute difference in centimetres) to the terminal.

## Results

### All 14 Constituents

![Full constituent comparison](comparison_full_constituents.png)

The upper panel shows the tidal water-level predictions from both libraries over January 2020. The predictions are visually indistinguishable at this scale. The lower panel shows the residual, which reveals a slowly modulated signal driven by the nodal corrections applied by utide but absent in uptide.

### M2 + S2 Only

![M2 and S2 comparison](comparison_m2s2_only.png)

Isolating the two dominant semi-diurnal constituents makes the effect of nodal corrections more visible. The residual retains the same low-frequency character, confirming that the difference is not an artefact of constituent superposition but originates from the nodal correction terms.

### Summary Statistics

| Scenario | RMSE (cm) | Max \|diff\| (cm) |
|---|---|---|
| All 14 constituents | 1.2025 | 2.7518 |
| M2 + S2 only | 0.6011 | 0.9591 |

Values computed for January 2020 at 10-minute intervals, latitude −50°.

## Notes on Conventions

When comparing or converting between the two libraries, keep the following in mind:

- **Phase convention**: utide uses Greenwich phase lags (degrees), which express the phase of the constituent relative to the Greenwich meridian. uptide accepts local phases in radians at the initial time. Converting between them requires accounting for the astronomical argument `V₀ + u` at the reference epoch.
- **Nodal corrections**: utide modulates each constituent's amplitude and phase using time- and latitude-dependent factors `f` (amplitude correction) and `u` (phase correction). uptide does not apply these corrections; the input amplitudes and phases are used as-is. This is the primary source of discrepancy between the two predictions.
- **Time input**: utide accepts Python `datetime` objects (converted internally to Gregorian datenums). uptide requires elapsed seconds from a user-specified reference datetime set via `set_initial_time()`.
- **Latitude**: utide requires a latitude for computing nodal corrections. For the Patagonia site, `lat = −50°` is used.

<!--
## License

This project is released under the [MIT License](https://opensource.org/licenses/MIT).
-->

## References

- Bowman, Wesley. *UTide* Python package. Available at: https://github.com/wesleybowman/UTide
- Kramer, Stephan. *uptide* Python package. Available at:  https://github.com/stephankraabel/uptide](https://github.com/stephankramer/uptide
