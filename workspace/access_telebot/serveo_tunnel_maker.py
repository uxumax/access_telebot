import subprocess
import re
import pty
import os
import select
import threading
import signal

if __name__ == "__main__":
    from logging import getLogger as get_logger
else:
    from access_telebot.logger import get_logger




class ServeoTunnelMaker:
    ssh_cmd = [
        'ssh', 
        '-o', 
        'ConnectTimeout=5', 
        '-R', 
        '80:localhost:8001', 
        'serveo.net'
    ]
    log = get_logger(__name__)
    pid: int

    @staticmethod
    def _get_serveo_host(fd):
        while True:
            # Setting up a timeout for os.read
            r, _, _ = select.select([fd], [], [], 10)  # 10 seconds timeout
            if r:
                line = os.read(fd, 1024).decode()
                if not line:
                    break
                print(line)
                match = re.search(r'https://[a-z0-9]+\.serveo\.net', line)
                if match:
                    url = match.group(0).strip()
                    return url
            else:
                # Timeout reached without reading any data
                print("Connection timeout or Serveo.net is not available.")
                return None

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

        thread = threading.Thread(target=target)
        thread.start()
        return thread

    def make(self):
        self.log.info("Make new serveo tunnel")
        master, slave = pty.openpty()
        thread = self._make_tunnel(slave)
        serveo_host = self._get_serveo_host(master)
        
        if serveo_host is None:
            self.log.error("Failed to create serveo tunnel.")
            os.kill(self.pid, signal.SIGTERM)  # Terminate the SSH process if failed to connect
            return None, None

        self.log.info(f"Has been made serveo tunnel {thread}:{serveo_host}")
        os.close(slave)
        os.close(master)
        thread.join()

        return self.pid, serveo_host

if __name__ == "__main__":
    pid, serveo_host = ServeoTunnelMaker().make()
    if pid and serveo_host:
        print(pid, serveo_host)
    else:
        print("Failed to establish tunnel.")
