# Parameterized UART Transceiver (Verilog)

A synthesizable 8-N-1 UART with a self-checking loopback testbench.

**Highlights**
- Baud generator, transmitter, and 16× oversampling receiver with start-bit re-centering, 3-sample majority-vote sampling, and framing-error detection.
- Parameterized by clock frequency, baud rate, and oversampling ratio.
- Self-checking testbench sends all 256 byte values + 256 random bytes: **512 bytes, 0 errors**; tolerates ±3% baud mismatch.

**Files**
- `rtl/` — baud_gen, uart_tx, uart_rx, uart_loopback
- `tb/tb_uart.v` — full self-checking testbench
- `design.sv`, `testbench.sv`, `testbench_demo.sv` — single-file versions (EDA Playground)
- `uart_frame.png` — annotated 8-N-1 frame
- `UART_Project_Overview.pdf` — one-page overview

Run (Icarus Verilog):
```
iverilog -g2012 -o sim rtl/*.v tb/tb_uart.v && vvp sim
```
