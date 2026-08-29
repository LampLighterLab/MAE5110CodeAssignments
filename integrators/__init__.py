# For more about init files, see https://realpython.com/python-init-py/
# and https://medium.com/data-science/whats-init-for-me-d70a312da583

# Keep package init side-effect free — do not eagerly import submodules
# (avoids circular import: integrators/__init__.py -> integrator_euler -> .integrator_base
#  while package is still initializing). Submodules are loaded on demand via
#  `from integrators import integrator_euler` or `from integrators.integrator_euler import ...`.

__all__ = ["integrator_base", "integrator_euler", "integrator_rk4"]
