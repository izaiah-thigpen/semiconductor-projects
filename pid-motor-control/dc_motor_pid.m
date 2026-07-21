%% DC Motor Speed Control with a PID Controller
%  Time-domain simulation of a brushed DC motor under closed-loop PID speed
%  control, compared against open-loop drive, including load-disturbance
%  rejection. Self-contained: uses only base MATLAB (no toolboxes required).
%
%  Author: Izaiah Thigpen

clear; clc; close all;

%% ---- Motor parameters (small brushed DC motor) ----
R  = 2.0;      % armature resistance (ohm)
L  = 0.5e-3;   % armature inductance (H)
Kt = 0.05;     % torque constant (N*m/A)
Ke = 0.05;     % back-EMF constant (V*s/rad)
J  = 1e-4;     % rotor inertia (kg*m^2)
b  = 1e-4;     % viscous friction (N*m*s)
Vmax = 12.0;   % supply voltage limit (V)

dcgain = Kt/(R*b + Kt*Ke);          % steady-state speed gain (rad/s per V)

%% ---- Setpoint, disturbance, timing ----
ref_rpm = 1000;                     % target speed (rpm)
ref     = ref_rpm*2*pi/60;          % target speed (rad/s)
T       = 1.0;                      % sim duration (s)
dt      = 1e-5;                     % integration step (s)
Ts      = 1e-3;                     % controller sample time (1 kHz)
Tload      = 0.02;                  % load torque applied (N*m)
Tload_time = 0.5;                   % time load is applied (s)

%% ---- PID gains ----
Kp = 0.4;  Ki = 25;  Kd = 0.002;

%% ---- Simulation ----
[t, w_cl, u_cl] = sim_motor(true,  0, ...
    R,L,Kt,Ke,J,b,Vmax,ref,T,dt,Ts,Tload,Tload_time,Kp,Ki,Kd);
[~, w_ol, ~   ] = sim_motor(false, ref/dcgain, ...  % open loop: fixed V for target at no load
    R,L,Kt,Ke,J,b,Vmax,ref,T,dt,Ts,Tload,Tload_time,Kp,Ki,Kd);

%% ---- Performance metrics (before the disturbance) ----
Nseg = round(0.49*numel(t));
seg  = w_cl(1:Nseg);
overshoot = (max(seg) - ref_rpm)/ref_rpm*100;
t10 = t(find(w_cl >= 0.1*ref_rpm, 1));
t90 = t(find(w_cl >= 0.9*ref_rpm, 1));
rise_ms = (t90 - t10)*1000;
band = 0.02*ref_rpm;
idx  = find(abs(seg - ref_rpm) > band, 1, 'last');
settle_ms = t(idx)*1000;
sse = ref_rpm - mean(w_cl(round(0.4*end):Nseg));
dstart = round(0.5*numel(t)); dend = round(0.6*numel(t));
dip = (ref_rpm - min(w_cl(dstart:dend)))/ref_rpm*100;

fprintf('\n--- Closed-loop step response ---\n');
fprintf('  Overshoot        : %.1f %%\n', overshoot);
fprintf('  Rise time (10-90): %.0f ms\n', rise_ms);
fprintf('  Settling (2%%)    : %.0f ms\n', settle_ms);
fprintf('  Steady-state err : %.2f rpm\n', sse);
fprintf('  Disturbance dip  : %.1f %% (recovers to setpoint)\n\n', dip);

%% ---- Plots ----
figure('Color','w','Position',[100 100 760 540]);

subplot(3,1,[1 2]); hold on; grid on;
yline(ref_rpm,'--','Color',[.5 .5 .5],'LineWidth',1);
plot(t, w_ol,'Color',[0.75 0.16 0.18],'LineWidth',1.3);
plot(t, w_cl,'Color',[0.10 0.31 0.48],'LineWidth',1.8);
xline(Tload_time,':','Color',[0.15 0.68 0.38],'LineWidth',1);
ylim([0 1150]); ylabel('Motor speed (rpm)');
title('DC Motor Speed Control — PID vs Open Loop','FontWeight','bold');
legend({'Reference (1000 rpm)','Open loop (fixed voltage)','Closed loop (PID)'}, ...
    'Location','southeast');
text(Tload_time+0.02, 300, 'load torque disturbance', 'Color',[0.15 0.68 0.38],'FontSize',9);

subplot(3,1,3); hold on; grid on;
plot(t, u_cl,'Color',[0.10 0.31 0.48],'LineWidth',1.2);
yline( Vmax,':','Color',[0.75 0.16 0.18]); yline(-Vmax,':','Color',[0.75 0.16 0.18]);
ylim([-13 13]); ylabel('Control (V)'); xlabel('Time (s)');

%% ================= local functions =================
function [t, w_rpm, u_log] = sim_motor(closed, Vfix, ...
        R,L,Kt,Ke,J,b,Vmax,ref,T,dt,Ts,Tload,Tload_time,Kp,Ki,Kd)
    n = round(T/dt); ce = round(Ts/dt);
    i = 0; w = 0; integ = 0; e_prev = 0; u = 0;
    t = zeros(n,1); w_rpm = zeros(n,1); u_log = zeros(n,1);
    for k = 1:n
        tt = (k-1)*dt;
        Tl = (tt >= Tload_time) * Tload;                 % load torque
        if closed && mod(k-1, ce) == 0                   % discrete PID update
            e = ref - w;
            deriv = (e - e_prev)/Ts;
            u_unsat = Kp*e + Ki*integ + Kd*deriv;
            u = min(Vmax, max(-Vmax, u_unsat));          % saturate
            if u == u_unsat                              % anti-windup clamp
                integ = integ + e*Ts;
            end
            e_prev = e;
        elseif ~closed
            u = Vfix;
        end
        di = (u - R*i - Ke*w)/L;                         % electrical
        dw = (Kt*i - b*w - Tl)/J;                         % mechanical
        i = i + di*dt;  w = w + dw*dt;                   % Euler integrate
        t(k) = tt;  w_rpm(k) = w*60/(2*pi);  u_log(k) = u;
    end
end
