import docker
import pexpect
import threading
import time


class Pyterpreted(object):
    def __init__(self, executable='', max_queued_commands=5, polling_sleep=1, expected_str='\n>>> '):
        super(Pyterpreted, self).__init__()
        self.command_queue = []
        self.result_queue = []
        self.max_queued_commands = max_queued_commands
        self.running = True
        self._polling_sleep = polling_sleep
        self._runner = pexpect.spawnu(executable)
        self._expected_str = expected_str
        self._runner.expect(self._expected_str)
        t = threading.Thread(target=self._run_next_command)
        t.start()

    def add_command(self, command):
        if len(self.command_queue) >= self.max_queued_commands:
            return False
        self.command_queue.append(command)
        return len(self.command_queue)

    def _run_next_command(self):
        while True:
            if self.running and len(self.command_queue) is not 0:
                command = self.command_queue.pop()
                print(f'Running command: {command}')
                if '\n' in command:
                    command += '\n'
                self._runner.sendline(command)
                self._runner.expect(self._expected_str)
                raw_result = self._runner.before
                if '\r\x1b[K>>> ' in raw_result:
                    raw_result = raw_result.split('\r\x1b[K>>> ')[1]
                new_element = {'input': command, 'result': f'>>> {raw_result}'}
                self.result_queue.append(new_element)
            else:
                time.sleep(self._polling_sleep)

    def get_output(self):
        while True:
            if len(self.result_queue) is 0:
                time.sleep(self._polling_sleep)
                yield None
            while len(self.result_queue) > 0:
                yield self.result_queue.pop(0)
