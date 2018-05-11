import io
import pexpect
import threading


class Pyterpreted(object):
    def __init__(self, executable):
        super(Pyterpreted, self).__init__()
        self.output = io.StringIO('')
        self.running = True
        self._runner = pexpect.spawnu(executable)
        self._runner_thread = threading.Thread(target=self._run_next_command)
        self._runner_thread.start()

    def add_command(self, command):
        return self._runner.sendline(command)

    def _run_next_command(self):
        while self._runner.expect('.+', timeout=None) is 0:
            self.output.write(self._runner.after)
