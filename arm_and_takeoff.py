import sys
import time
from pymavlink import mavutil

def main():
    print("Connecting to vehicle...")
    master = mavutil.mavlink_connection('udpin:127.0.0.1:14551')
    master.wait_heartbeat()
    print("Heartbeat received!")

    # Switch to GUIDED mode
    # Standard custom mode for ArduCopter GUIDED is 4
    # master.set_mode_by_name('GUIDED') can be used, but sometimes mode_mapping fails if heartbeat has not defined it
    # Let's use command_long to set mode
    # MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = 1
    # Base mode or custom mode?
    # pymavlink master has master.set_mode('GUIDED') or master.mode_mapping()
    try:
        master.set_mode('GUIDED')
        print("Set mode to GUIDED")
    except Exception as e:
        print(f"Error setting mode: {e}")
        # fallback
        master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4 # GUIDED
        )
        print("Sent fallback GUIDED mode")

    time.sleep(1)

    # Arm vehicle
    print("Arming vehicle...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, # 1 to arm, 0 to disarm
        0, 0, 0, 0, 0, 0
    )

    # Wait for arming confirmation
    armed = False
    for _ in range(10):
        master.wait_heartbeat()
        # check if armed
        if master.motors_armed():
            print("Vehicle armed!")
            armed = True
            break
        time.sleep(0.5)

    if not armed:
        print("Failed to arm vehicle.")
        sys.exit(1)

    # Takeoff
    altitude = 10.0
    print(f"Taking off to {altitude} meters...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0, 0, 0,
        altitude
    )

    # Verify takeoff sent
    print("Takeoff command sent successfully.")

if __name__ == '__main__':
    main()
