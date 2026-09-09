# Dev journal

## 2026-09-08 — phase edit — assignment_0 caller aligned with model/integrator contracts (pass)
Plan: `doc/plans/assignment_0_update_plan.md` (finished; archived from `.opencode/workspace/plans/`)

### Context
`assignments/assignment_0/assignment_0.py` still called the old module-function contract (`dynamics_function=`, module-level `calculate_energy`) after models/integrators moved to instance contracts; RK4 also carried a model-specific print and 2-arg callback.

### Plan
Caller-only update: instantiate `ModelPendulum`/`ModelBouncingBall`, pass `model=` to `integrate()`, use instance `calculate_energy`, keep defaults/comments; align Euler+RK4 checkpoint callbacks to 5-arg `(t1, s1, t2, s2, model)`; phase print becomes a commented demo callback.

### Files-to-edit
- `assignments/assignment_0/assignment_0.py`
- `integrators/integrator_euler.py`
- `integrators/integrator_rk4.py`

### Result
V1 ball/RK4 default (dt=1e-2): ratio 1.00015951 → 0.016% (pass, <1%). V2 pendulum/RK4 dt=1e-3 script params: ratio 1.00000000 (pass). V3 signature smoke: pass. 5-arg callback fires on both integrators with model forwarded.

### Files-changed
- `assignments/assignment_0/assignment_0.py` (model instances, `model=` call, instance energy, demo callback comment)
- `integrators/integrator_euler.py` (forward `model` in callback)
- `integrators/integrator_rk4.py` (removed print, 5-arg callback)
- `.opencode/workspace/plans/assignment_0_update_plan.md` (Exec header + V1..V3 results)

### Notes
- Plain `uv run python assignments/assignment_0/assignment_0.py` fails with `ModuleNotFoundError: No module named 'integrators'` (script move off root broke imports); verified with `PYTHONPATH=.`. Fix (bootstrap vs docs) left for user decision.
- Model `generate_params()` defaults carry `damping_coeff 0.1` (pendulum), which bleeds ~86% energy over 5s; script's explicit `damping 0.0` params are load-bearing for the <1% criterion.

## [2026-09-08] Energy-conservation pytest (bouncing ball, Euler + RK4)

### Context
No tests existed (`pytest` dev dep, zero `test_*.py`); agreed layout A with a single energy test, scope confined to `tests/`, ball with zero ground damping, `dt=1e-5`, `sim 5s`, `<1%` loss for both integrators.

### Plan
1. Create `tests/test_energy_conservation.py` parametrized over `IntegratorEuler`/`IntegratorRK4`.
2. Run `uv run pytest tests/test_energy_conservation.py -v`.
3. Log result here; no source/config edits.

#### Files to edit
| File | Change |
|------|--------|
| `tests/test_energy_conservation.py` | new parametrized energy-conservation test |

### Result
✅

2 passed in 5.76s (`test_energy_conservation[IntegratorEuler]`, `[IntegratorRK4]`).

#### Files changed
| File | Change |
|------|--------|
| `tests/test_energy_conservation.py` | new file (params/initial state mirror `assignment_0.py` ball selection; `(2, N)` energy check) |

### Notes
- Pre-existing `discrete_jump` abstract-blocker already fixed by user (no-op overrides in both models), so tests-only scope held.
- `dt=1e-5 x 5s` = 500001 points runs in ~6s total; no speed-up needed.
