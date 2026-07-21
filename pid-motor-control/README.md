# DC Motor PID Speed Controller (MATLAB)

Time-domain simulation of a brushed DC motor under closed-loop PID speed control,
built from first principles (no toolboxes required).

**Highlights**
- Models coupled electrical + mechanical dynamics; discrete 1 kHz PID with output saturation and integral anti-windup.
- Tuned response: 6% overshoot, 38 ms rise, <100 ms settling, zero steady-state error.
- Rejects a step load-torque disturbance (setpoint held within 1%) where open-loop drive droops.

**Files**
- `dc_motor_pid.m` — simulation + plots + printed metrics
- `pid_response.png` — speed response and control effort
- `PID_Project_Overview.pdf` — one-page overview

Run: open `dc_motor_pid.m` in MATLAB and press Run.
