import os

from netqasm.runtime.application import app_instance_from_path, network_cfg_from_path
from squidasm.run.simulate import simulate_application

# APP_DIR = "../netqasm/netqasm/examples/apps/teleport"
# APP_DIR = "../netqasm/netqasm/examples/apps/bb84"
APP_DIR = "../netqasm/netqasm/examples/apps/blind_grover"

if __name__ == "__main__":
    app_instance = app_instance_from_path(APP_DIR)
    # network_cfg = network_cfg_from_path(APP_DIR)

    # simulate_application(app_instance, 3, network_cfg)
    simulate_application(app_instance, 3)
