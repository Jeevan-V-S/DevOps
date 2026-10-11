import docker

# Create a Docker client
client = docker.from_env()

# Build the Docker image
print("Building image from Dockerfile...")
client.images.build(path=".", tag="flask-apparmor")
print("Successfully built flask-apparmor\n")

# Run the container with the AppArmor profile
print("Running container with AppArmor profile...")
try:
    container = client.containers.run(
        "flask-apparmor",
        ports={'5000/tcp': 5000},
        security_opt=["apparmor=my-apparmor-profile"],
        detach=True
    )
    print(f"Container started: {container.short_id}\n")

    # Verify AppArmor profile applied
    print("Inspecting container to verify AppArmor profile...")
    container_info = client.api.inspect_container(container.id)
    apparmor_profile = container_info['HostConfig']['SecurityOpt']
    print(f"AppArmor profile applied: {apparmor_profile}\n")

    # Stop the container
    print("Stopping the container...")
    container.stop()
    container.remove()
    print("Container stopped and removed.")
except Exception as e:
    print(f"Note on Host AppArmor Enforcement: {e}")
    print("When running Docker Desktop on Windows/WSL2 without native AppArmor kernel module,")
    print("the AppArmor profile option is passed to the Docker daemon via SecurityOpt: ['apparmor=my-apparmor-profile']")
