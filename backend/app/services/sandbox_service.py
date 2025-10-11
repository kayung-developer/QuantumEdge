"""
AuraQuant - Docker Sandbox Management Service
"""
import docker
import base64
import json
from docker.errors import ContainerError, ImageNotFound, APIError


class SandboxExecutionService:
    def __init__(self):
        try:
            self.client = docker.from_env()
            # The image name and tag must match how you build it
            self.image_name = "auraquant-sandbox:latest"
        except Exception as e:
            print(f"Docker is not available or configured correctly. Sandbox service will be disabled. Error: {e}")
            self.client = None

    async def run_in_sandbox(self, user_code: str, data_df_json: str, params_json: str, symbol: str) -> dict:
        """
        Runs a backtest inside a new, isolated Docker container.
        """
        if not self.client:
            raise RuntimeError("Docker service is not available.")

        # Base64 encode all inputs to safely pass them as command-line arguments
        user_code_b64 = base64.b64encode(user_code.encode('utf-8')).decode('ascii')
        data_df_json_b64 = base64.b64encode(data_df_json.encode('utf-8')).decode('ascii')
        params_json_b64 = base64.b64encode(params_json.encode('utf-8')).decode('ascii')
        symbol_b64 = base64.b64encode(symbol.encode('utf-8')).decode('ascii')

        command = [user_code_b64, data_df_json_b64, params_json_b64, symbol_b64]

        container = None
        try:
            # Run the container. This is a blocking call, so in a real high-throughput
            # system, you'd run this in a thread pool executor.
            container = self.client.containers.run(
                self.image_name,
                command=command,
                detach=False,  # Run and wait for it to finish
                remove=True,  # Automatically remove the container when done
                # --- Resource Limits ---
                # This is a critical security feature to prevent resource exhaustion attacks.
                mem_limit="512m",
                cpu_quota=50000,  # 50% of one CPU core
                # Disable networking for extra security
                network_disabled=True,
            )
            # The output will be a byte string, decode it
            output = container.decode('utf-8')
            return json.loads(output)

        except ContainerError as e:
            # Error from within the container's script
            return {"success": False, "error": "Execution failed inside the sandbox.", "details": e.stderr.decode()}
        except ImageNotFound:
            return {"success": False, "error": f"Sandbox image '{self.image_name}' not found. Please build it."}
        except APIError as e:
            return {"success": False, "error": "Docker API error.", "details": str(e)}
        finally:
            # Ensure container is removed even if there's an error above `run`
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass


sandbox_service = SandboxExecutionService()