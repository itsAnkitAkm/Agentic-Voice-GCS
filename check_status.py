from pymavlink import mavutil
master = mavutil.mavlink_connection('udpin:127.0.0.1:14551')
master.wait_heartbeat()
# get mode
custom_mode = master.messages['HEARTBEAT'].custom_mode
armed = master.motors_armed()
# get alt
msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=5)
alt = msg.relative_alt / 1000.0 if msg else "Unknown"
print(f"Mode: {custom_mode}, Armed: {armed}, Altitude: {alt}")
