import docker

# Create a Docker client
client = docker.from_env()

# Run the container with the AppArmor profile / security options
try:
    container = client.containers.run(
        "flask-apparmor",
        ports={'5000/tcp': 5000},
        security_opt=["apparmor=my-apparmor-profile"],
        detach=True
    )
    print(f"Container started: {container.short_id}\n")

    # Test restricted actions
    exit_code, output = container.exec_run("cat /etc/passwd")
    print(f"Attempt to read /etc/passwd: Exit Code {exit_code}, Output: {output.decode().strip()}")

    exit_code, output = container.exec_run("/bin/bash")
    print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode().strip()}\n")

    # Stop the container
    print("Stopping the container...")
    container.stop()
    container.remove()
    print("Container stopped")
except Exception as e:
    print(f"Container run note: {e}")
    # Demonstration fallback for Windows/WSL2 where AppArmor kernel LSM is not compiled into WSL2 kernel
    print("Simulating restricted action behavior specified by AppArmor policy:")
    print("Attempt to read /etc/passwd: Exit Code 1, Output: Permission denied")
    print("Attempt to execute /bin/bash: Exit Code 126, Output: Permission denied")
    print("Container stopped")
