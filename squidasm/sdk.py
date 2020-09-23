from threading import Thread

from netqasm.sdk import NetQASMConnection
from netqasm.subroutine import PreSubroutine, Subroutine
from netqasm.parsing.text import assemble_subroutine
from netqasm.instructions.flavour import NVFlavour
from netqasm.compiling import NVSubroutineCompiler
from squidasm.queues import get_queue
from squidasm.backend.glob import get_node_id_for_app, get_node_name, get_running_backend


class NetSquidConnection(NetQASMConnection):

    def __init__(
        self,
        node_name,
        app_id=None,
        max_qubits=5,
        log_config=None,
        epr_sockets=None,
        compiler=None,
    ):
        self._message_queue = get_queue(node_name)
        super().__init__(
            name=node_name,
            app_id=app_id,
            max_qubits=max_qubits,
            log_config=log_config,
            epr_sockets=epr_sockets,
            compiler=compiler,
        )

    def _commit_serialized_message(self, raw_msg, block=True, callback=None):
        """Commit a message to the backend/qnodeos"""
        self._message_queue.put(raw_msg)
        if block:
            self._execute_callback(item=raw_msg, callback=callback)
        else:
            # Execute callback in a new thread after the subroutine is finished
            thread = Thread(target=self._execute_callback, args=(raw_msg, callback,))
            thread.daemon = True
            thread.start()

    def _execute_callback(self, item, callback=None):
        self.block(item=item)
        if callback is not None:
            callback()

    def block(self, item=None):
        """Block until flushed subroutines finish"""
        if item is None:
            self._message_queue.join()
        else:
            self._message_queue.join_task(item=item)

    def _get_node_id(self, node_name):
        """Returns the node id for the node with the given name"""
        return get_node_id_for_app(app_name=node_name)

    def _get_node_name(self, node_id):
        """Returns the node name for the node with the given ID"""
        return get_node_name(node_id=node_id)

    def _pre_process_subroutine(self, pre_subroutine: PreSubroutine) -> Subroutine:
        """Parses and assembles the subroutine.
        """
        subroutine: Subroutine = assemble_subroutine(pre_subroutine)
        if self._compiler is not None:
            subroutine = self._compiler(subroutine=subroutine).compile()
        else:
            backend = get_running_backend()
            subroutine_handler = backend.subroutine_handlers[self.name]
            flavour = subroutine_handler.flavour
            if isinstance(flavour, NVFlavour):
                self._logger.info("Compiling subroutine to NV flavour")
                subroutine = NVSubroutineCompiler(subroutine=subroutine).compile()

        if self._track_lines:
            self._log_subroutine(subroutine=subroutine)
        return subroutine
