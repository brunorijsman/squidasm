from netqasm.sdk import Qubit
from netqasm.sdk import ThreadSocket as Socket
from squidasm.sdk import NetSquidConnection
from netqasm.logging import get_netqasm_logger

from shared.myfuncs import custom_recv, custom_measure

logger = get_netqasm_logger()


def main(app_config=None):
    socket = Socket("bob", "alice", log_config=app_config.log_config)

    # Initialize the connection to the backend
    bob = NetSquidConnection(
        app_name=app_config.app_name,
		node_name=app_config.node_name,
        log_config=app_config.log_config
    )
    with bob:
        q = Qubit(bob)
        custom_measure(q)

    socket.recv()
    custom_recv(socket)


if __name__ == "__main__":
    main()
