"""
uptide_vs_utide.py
==================
Comparison of tidal prediction between two Python libraries:
  - utide  : Python port of the MATLAB UTide toolbox (Codiga 2011)
  - uptide : Lightweight tidal prediction library

The script uses harmonic tidal constituents (amplitude & phase) from a site
in Patagonia to reconstruct water-surface elevation over one month (January 2020)
at 10-minute intervals. Two comparisons are made:

  1. Full set of 14 constituents — comparing utide vs uptide predictions.
  2. Reduced set (M2 + S2 only)  — isolating the dominant semi-diurnal signal
     to more clearly assess agreement between the two libraries.

Key differences between the libraries:
  - utide  : expects time as matplotlib datenums; phases as Greenwich phase lags
             [degrees]; applies nodal corrections (f, u, V) that depend on
             latitude and time. lat=-50 is used here for the Patagonia site.
  - uptide : expects elapsed time in seconds from a reference; phases in radians
             (interpreted as local phase at t=0, no nodal corrections applied).
  - Because of these different phase conventions and the presence/absence of
    nodal corrections, some residual difference between the two predictions is
    expected and physically meaningful.
"""

# ---------------------------------------------------------------------------
# Libraries
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import utide
from utide.utilities import Bunch
from utide._ut_constants import ut_constants, constit_index_dict
from utide._time_conversion import _python_gregorian_datenum
import uptide
from matplotlib import rc

rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica'], 'size': 12})
#rc('text', usetex=True)
#plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# ---------------------------------------------------------------------------
# Helper — build a utide coef structure from known amplitudes and phases
# ---------------------------------------------------------------------------

def build_utide_coef(names, amp, pha_deg, reftime, lat=0.0):
    """
    Construct a utide-compatible coefficient structure (Bunch) from known
    tidal amplitudes and phases, suitable for use with utide.reconstruct().

    Parameters
    ----------
    names    : array-like of str   -- constituent names (e.g. ['M2', 'S2'])
    amp      : array-like of float -- amplitudes [m]
    pha_deg  : array-like of float -- phases [degrees, Greenwich convention]
    reftime  : datetime            -- reference time (start of the time series)
    lat      : float               -- latitude [degrees]; controls nodal corrections

    Returns
    -------
    coef : Bunch  -- utide coefficient structure
    """
    names = np.asarray(names)
    n = len(names)

    # Look up internal utide indices and frequencies (cycles per hour) for
    # each constituent from utide's built-in constant database
    const = ut_constants.const
    lind = np.array([constit_index_dict[nm] for nm in names])
    frq  = const.freq[lind]   # cycles per hour

    return Bunch(
        name=names,
        A=np.asarray(amp, dtype=float),
        g=np.asarray(pha_deg, dtype=float),
        A_ci=np.zeros(n),   # confidence intervals -- not available, set to zero
        g_ci=np.zeros(n),
        mean=0.0,            # no mean offset
        slope=0.0,           # no secular trend
        aux=Bunch(
            reftime=_python_gregorian_datenum(reftime),  # days since 0000-12-31 (utide convention)
            lat=float(lat),
            frq=frq,         # constituent frequencies [cycles per hour]
            lind=lind,       # indices into utide's internal constants table
            opt=Bunch(
                twodim=False,       # scalar (h) reconstruction, not vector (u,v)
                notrend=True,       # no secular trend
                nodiagn=True,       # skip SNR/PE diagnostics
                nodsatlint=False,   # apply nodal satellite corrections (linear interp)
                nodsatnone=False,
                gwchlint=False,     # apply Greenwich correction (linear interp)
                gwchnone=False,
                prefilt=[],         # no pre-filter
                conf_int='none',    # skip confidence interval computation
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Tidal constituent data (Patagonia site)
# ---------------------------------------------------------------------------
# Each row: (name, frequency [cpd], amplitude [m], phase [degrees])
data_raw = np.array([
    (b'O1  ', 0.0387, 0.09604166,  -58.62699486),
    (b'K1  ', 0.0418, 0.21723029,   -2.63849183),
    (b'N2  ', 0.0790, 0.59854657,   23.95276959),
    (b'M2  ', 0.0805, 2.86359250,   63.87340555),
    (b'S2  ', 0.0833, 0.55020451,  141.56787744),
    (b'2N2 ', 0.0775, 0.09402127,  -91.21887524),
    (b'MF  ', 0.0031, 0.00921954, -167.47119229),
    (b'MM  ', 0.0015, 0.00509902, -168.69006753),
    (b'Q1  ', 0.0372, 0.00282843, -135.00000000),
    (b'P1  ', 0.0416, 0.05223983,   -5.49232456),
    (b'K2  ', 0.0836, 0.15500000,  143.13010235),
    (b'MS4 ', 0.1638, 0.01664332,  147.26477373),
    (b'MN4 ', 0.1595, 0.00583095,   30.96375653),
    (b'M4  ', 0.1610, 0.02906888,   93.94518623),
], dtype=[('constituent', 'S13'), ('freq', '<f8'), ('amp', '<f8'), ('pha', '<f8')])

# Strip trailing whitespace from byte-string names and convert to plain strings
names_full = np.char.strip(data_raw['constituent'].astype('U13'))

# ---------------------------------------------------------------------------
# Time axes
# ---------------------------------------------------------------------------
start_t = datetime(2020, 1, 1)
end_t   = datetime(2020, 2, 1)
dt_min  = 10   # minutes

# Datetime array (used for plotting and utide)
time_array = np.arange(start_t, end_t, timedelta(minutes=dt_min)).astype(datetime)

# Elapsed seconds from start — required by uptide
dt_sec       = dt_min * 60
time_seconds = np.arange(0, len(time_array) * dt_sec, dt_sec, dtype=float)


# ===========================================================================
# SECTION 1 — Full constituent set: utide vs uptide
# ===========================================================================

# --- utide prediction -------------------------------------------------------
coef_full = build_utide_coef(
    names_full,
    data_raw['amp'],
    data_raw['pha'],
    reftime=start_t,
    lat=-50.0,  # approximate latitude of the Patagonia site
)
result_utide_full = utide.reconstruct(time_array, coef_full, verbose=False)
elev_utide_full   = result_utide_full['h']

# --- uptide prediction -------------------------------------------------------
# uptide requires phase in radians; does not apply nodal corrections
tide_full = uptide.Tides(names_full)
tide_full.set_initial_time(start_t)
elev_uptide_full = tide_full.from_amplitude_phase(
    data_raw['amp'],
    np.deg2rad(data_raw['pha']),
    time_seconds,
)

# --- Plot -------------------------------------------------------------------
residual_full = elev_utide_full - elev_uptide_full[:len(time_array)]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

ax1.plot(time_array, elev_utide_full,                    label='UTide',  lw=1.5)
ax1.plot(time_array, elev_uptide_full[:len(time_array)], label='uptide', lw=2.5, color='C1', ls='--' , alpha=0.9)
ax1.set_title('Tidal prediction — all 14 constituents (Patagonia)')
ax1.set_ylabel('Water level (m)')
ax1.legend()
ax1.set_xlim(time_array[0], time_array[-1])

rmse_full   = np.sqrt(np.nanmean(residual_full**2))
maxdiff_full = np.nanmax(np.abs(residual_full))

ax2.plot(time_array, residual_full, color='C2', lw=1.0)
ax2.axhline(0, color='k', lw=0.7, ls='--')
ax2.set_title('Residual (UTide - uptide)')
ax2.set_xlabel('Time')
ax2.set_ylabel('Residual (m)')
ax2.set_xlim(time_array[0], time_array[-1])
ax2.text(0.01, 0.92, f'RMSE = {rmse_full*100:.3f} cm  |  Max |diff| = {maxdiff_full*100:.3f} cm',
         transform=ax2.transAxes, fontsize=10, va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='grey', alpha=0.8))

plt.tight_layout()
plt.savefig('comparison_full_constituents.png', dpi=150)
plt.show()


# ===========================================================================
# SECTION 2 — Reduced set (M2 + S2 only)
# ===========================================================================

# Filter the data to M2 and S2 only
df    = pd.DataFrame(data_raw)
mask  = df['constituent'].isin([b'M2  ', b'S2  '])
data_m2s2  = df[mask]
names_m2s2 = np.char.strip(data_m2s2['constituent'].values.astype('U13'))

# --- utide prediction -------------------------------------------------------
coef_m2s2 = build_utide_coef(
    names_m2s2,
    data_m2s2['amp'].values,
    data_m2s2['pha'].values,
    reftime=start_t,
    lat=-50.0,
)
result_utide_m2s2 = utide.reconstruct(time_array, coef_m2s2, verbose=False)
elev_utide_m2s2   = result_utide_m2s2['h']

# --- uptide prediction -------------------------------------------------------
tide_m2s2 = uptide.Tides(names_m2s2)
tide_m2s2.set_initial_time(start_t)
elev_uptide_m2s2 = tide_m2s2.from_amplitude_phase(
    data_m2s2['amp'].values,
    np.deg2rad(data_m2s2['pha'].values),
    time_seconds,
)

# --- Plot -------------------------------------------------------------------
residual_m2s2 = elev_utide_m2s2 - elev_uptide_m2s2[:len(time_array)]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

ax1.plot(time_array, elev_utide_m2s2,                    label='UTide (M2+S2)',  lw=1.5)
ax1.plot(time_array, elev_uptide_m2s2[:len(time_array)], label='uptide (M2+S2)', lw=2.5, color='C1', ls='--', alpha=0.9)
ax1.set_title('Tidal prediction — M2 + S2 constituents only (Patagonia)')
ax1.set_ylabel('Water level (m)')
ax1.legend()
ax1.set_xlim(time_array[0], time_array[-1])

rmse_m2s2    = np.sqrt(np.nanmean(residual_m2s2**2))
maxdiff_m2s2 = np.nanmax(np.abs(residual_m2s2))

ax2.plot(time_array, residual_m2s2, color='C2', lw=1.0)
ax2.axhline(0, color='k', lw=0.7, ls='--')
ax2.set_title('Residual (UTide - uptide)')
ax2.set_xlabel('Time')
ax2.set_ylabel('Residual (m)')
ax2.set_xlim(time_array[0], time_array[-1])
ax2.text(0.01, 0.92, f'RMSE = {rmse_m2s2*100:.3f} cm  |  Max |diff| = {maxdiff_m2s2*100:.3f} cm',
         transform=ax2.transAxes, fontsize=10, va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='grey', alpha=0.8))

plt.tight_layout()
plt.savefig('comparison_m2s2_only.png', dpi=150)
plt.show()


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------
print("\n=== Difference between UTide and uptide ===")
print("Note: residual differences are expected — utide applies nodal corrections")
print("and uses Greenwich phase lags, while uptide uses local phase with no nodal corrections.")
print(f"Full constituents  -- RMSE: {rmse_full*100:.4f} cm  |  Max |diff|: {maxdiff_full*100:.4f} cm")
print(f"M2 + S2 only       -- RMSE: {rmse_m2s2*100:.4f} cm  |  Max |diff|: {maxdiff_m2s2*100:.4f} cm")
