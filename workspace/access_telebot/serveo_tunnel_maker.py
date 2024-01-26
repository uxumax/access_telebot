import subprocess
import re
import pty
import os
from access_telebot.logger import get_logger
import threading


class ServeoTunnelMaker:
    ssh_cmd = ['ssh', '-R', '80:localhost:8001', 'serveo.net']
    log = get_logger(__name__)
    pid: int

    @staticmethod
    def _get_serveo_host(fd):
        while True:
            line = os.read(fd, 1024).decode()
            if not line:
                break

            match = re.search(r'https://[a-z0-9]+\.serveo\.net', line)
            if match:
                url = match.group(0).strip()
                # print(f"Найденный URL: {url}")
                return url

    def _make_tunnel(self, slave):
        # Запуск процесса SSH
        def target():
            process = subprocess.Popen(
                self.ssh_cmd,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                text=True
            )
            self.pid = process.pid

        # return process.pid
        thread = threading.Thread(target=target)
        thread.start()
        return thread

    def make(self):
        self.log.info(
            "Make new serveo tunnel"
        )

        master, slave = pty.openpty()
        thread = self._make_tunnel(slave)
        serveo_host = self._get_serveo_host(master)
        
        self.log.info(
            f"Has been made serveo tunnel {thread}:{serveo_host}"
        )

        os.close(slave)
        os.close(master)
        thread.join()

        return self.pid, serveo_host


if __name__ == "__main__":
    pid, serveo_host = ServeoTunnelMaker().make()
    print(pid, serveo_host)