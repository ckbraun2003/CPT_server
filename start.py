import subprocess
import sys
import signal
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("console.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ServerRunner:
    def __init__(self, scripts):
        """
        Initialize with a list of script paths
        Args:
            scripts: List of script paths or list of dicts with script info
        """
        print(f"DEBUG: Received scripts: {scripts}")
        print(f"DEBUG: Scripts type: {type(scripts)}")

        if not isinstance(scripts, list):
            raise TypeError(f"scripts must be a list, got {type(scripts)}")

        self.scripts = []
        for i, script in enumerate(scripts):
            print(f"DEBUG: Processing script {i}: {script} (type: {type(script)})")

            if isinstance(script, str):
                # Simple string path
                self.scripts.append({"path": script, "name": Path(script).stem})
            elif isinstance(script, dict):
                # Dict with path and name
                if "path" not in script:
                    raise ValueError(f"Script dict must have 'path' key, got: {script}")
                if "name" not in script:
                    script["name"] = Path(script["path"]).stem
                self.scripts.append(script)
            else:
                raise TypeError(f"Each script must be a string or dict, got {type(script)} for item {i}: {script}")

        print(f"DEBUG: Final scripts config: {self.scripts}")
        self.processes = {}  # {script_name: process}

    def check_scripts_exist(self):
        """Check if all target scripts exist"""
        all_exist = True
        for script in self.scripts:
            script_path = script["path"]
            if not Path(script_path).exists():
                logger.error(f"Script not found: {script_path}")
                all_exist = False
            else:
                logger.info(f"Found script: {script_path}")
        return all_exist

    def start_server(self, script_info):
        """Start a single server script"""
        script_path = script_info["path"]
        script_name = script_info["name"]

        try:
            # Convert to absolute path for better error handling
            abs_script_path = Path(script_path).resolve()

            logger.info(f"Starting server: {script_name}")
            logger.info(f"Script path: {abs_script_path}")
            logger.info(f"Python executable: {sys.executable}")

            process = subprocess.Popen(
                [sys.executable, str(abs_script_path)],
                cwd=Path(script_path).parent  # Set working directory to script's folder
            )
            self.processes[script_name] = process
            logger.info(f"Server started successfully: {script_name} (PID: {process.pid})")
            return process
        except FileNotFoundError as e:
            logger.error(f"File not found for {script_name}: {e}")
            logger.error(f"Tried to run: {sys.executable} {abs_script_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to start {script_name}: {e}")
            return None

    def monitor_processes(self):
        """Monitor running processes and log any failures"""
        while self.processes:
            terminated_scripts = []

            for script_name, process in self.processes.items():
                if process.poll() is not None:
                    # Process has terminated
                    if process.returncode == 0:
                        logger.info(f"Server {script_name} terminated normally")
                    else:
                        logger.error(f"Server {script_name} crashed with exit code {process.returncode}")
                        # Log stderr if available
                        try:
                            stderr = process.stderr.read()
                            if stderr:
                                logger.error(f"Error output from {script_name}: {stderr}")
                        except:
                            pass

                    terminated_scripts.append(script_name)

            # Remove terminated processes
            for script_name in terminated_scripts:
                del self.processes[script_name]

            if not self.processes:
                logger.info("All servers have stopped")
                return

            time.sleep(2)  # Check every 2 seconds

    def stop_all_servers(self):
        """Stop all running servers gracefully"""
        if not self.processes:
            return

        logger.info(f"Stopping {len(self.processes)} servers...")

        for script_name, process in self.processes.items():
            try:
                logger.info(f"Terminating {script_name} (PID: {process.pid})")
                process.terminate()

                # Wait up to 5 seconds for graceful shutdown
                try:
                    process.wait(timeout=5)
                    logger.info(f"Server {script_name} terminated gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"Server {script_name} didn't terminate, forcing kill")
                    process.kill()
                    process.wait()

            except Exception as e:
                logger.error(f"Error stopping {script_name}: {e}")

        self.processes.clear()

    def get_running_servers(self):
        """Get list of currently running servers"""
        return list(self.processes.keys())

    def run(self):
        """Main execution method"""
        logger.info(f"Preparing to start {len(self.scripts)} servers")

        if not self.check_scripts_exist():
            logger.error("Cannot start servers - some scripts not found")
            return False

        try:
            # Start all servers
            failed_servers = []
            for script_info in self.scripts:
                process = self.start_server(script_info)
                if not process:
                    failed_servers.append(script_info["name"])

            if failed_servers:
                logger.error(f"Failed to start servers: {', '.join(failed_servers)}")
                if not self.processes:
                    logger.error("No servers started successfully")
                    return False
                else:
                    logger.info(f"Continuing with {len(self.processes)} successfully started servers")

            running_servers = self.get_running_servers()
            logger.info(f"Successfully started servers: {', '.join(running_servers)}")
            logger.info("Press Ctrl+C to stop all servers")

            # Monitor processes
            self.monitor_processes()

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.stop_all_servers()
            logger.info("Server runner shutting down")

        return True


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    raise KeyboardInterrupt


def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Configure your scripts here
    scripts = [
        {"path": "src/mcp_server/main.py", "name": "MCP Server"},
        {"path": "src/web_server/main.py", "name": "Web Server"}
    ]

    # Create and run server manager
    runner = ServerRunner(scripts)
    runner.run()


if __name__ == "__main__":
    main()