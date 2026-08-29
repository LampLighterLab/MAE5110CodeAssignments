# AGENTS.md

## Scope
- Only use files inside this workspace (`MAE5110CodeAssignments/`). Do not read parent directories, sibling courses, or anything outside the workspace unless the user explicitly tells you to.

## Build & Run
- Requires Python `>=3.14`. Env manager is `uv` (`pyproject.toml:6`, `uv.lock:3`).
- Setup: `uv sync --python 3.14` — creates `.venv` (gitignored).
- Run inside env: `uv run python assignment_0.py` (see `README.md:9-16`).
- Tests (dev group): `uv run pytest` / `uv run pytest <path>::<test>` — `pytest` is the only dev dependency (`pyproject.toml:12-15`). No lint/typecheck/formatter config in repo.

## Structure
- `assignment_0.py` — entry script; explicit Euler loop + energy plot. Imports `models.pendulum` (`assignment_0.py:4`).
- `models/pendulum.py` — `dynamics(t, state, params)`, `calculate_energy(state, params)`, `generate_params()` (`models/pendulum.py:4,22,32`). State shape `(2,)` or `(2, N)` vectorized.
- `integrators/` — `integrator_base.py:3` `IntegratorBase.integrate(param_integrator, param_model, time_trajectory, initial_state)` is the contract. `integrator_euler.py` and `integrator_rk4.py` are stubs — implement there. Import as `from integrators import integrator_euler` etc. (`integrators/__init__.py:4`).
- `assignment_0.md` — spec for Euler/RK4 encapsulation and bouncing-ball task.

## Conventions
- Params are plain `dict`s (`gravity`, `length`, `mass`, `damping_coeff`) — see `models/pendulum.py:22-28` and `assignment_0.py:8-13`.
- Follow existing style: `snake_case` for functions/vars, `PascalCase` for integrator classes.

## OpenCode
- Config at `.opencode/opencode.json:3` points `instructions` to this file (`../AGENTS.md` relative to `.opencode/`). Skills paths: `.opencode/skills` + `.opencode/workspace/skills`.
- Available skills: `agents-bootstrap` (bootstrap/sync this file from `.opencode/AGENTS.md.template`), `research-notes`, `dev-journal`. Load via `skill` tool, not by guessing.
- After changing `opencode.json`, skills, or this file, restart opencode.
