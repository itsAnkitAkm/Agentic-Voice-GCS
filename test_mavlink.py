from pymavlink import mavutil

print("Connecting to SITL...")

vehicle = mavutil.mavlink_connection(
    "udpin:127.0.0.1:14551"
)

print("Waiting for heartbeat...")

vehicle.wait_heartbeat()

print(
    f"Connected to system {vehicle.target_system}, "
    f"component {vehicle.target_component}"
)

while True:
    message = vehicle.recv_match(
        type=["HEARTBEAT", "GLOBAL_POSITION_INT", "SYS_STATUS"],
        blocking=True
    )

    if message:
        print(message)