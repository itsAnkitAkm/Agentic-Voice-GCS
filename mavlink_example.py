from pymavlink import mavutil

vehicle = mavutil.mavlink_connection(
    "udpin:127.0.0.1:14551"
)

print("Waiting for heartbeat...")
vehicle.wait_heartbeat()

msg = vehicle.recv_match(
    type="GLOBAL_POSITION_INT",
    blocking=True,
    timeout=5
)

if msg:
    altitude = msg.relative_alt / 1000.0
    print(f"Altitude: {altitude:.2f} meters")
else:
    print("No altitude data received")