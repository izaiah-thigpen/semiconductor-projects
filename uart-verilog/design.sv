// ============================================================
// design.sv  —  Parameterized UART (8-N-1) transceiver
// Paste into the DESIGN pane on EDA Playground.
// Contains: baud_gen, uart_tx, uart_rx, uart_loopback
// ============================================================

// Baud-rate generator: emits a 1-clock 'tick' pulse at BAUD*OSR (the RX
// oversampling rate). TX and RX both derive bit timing by counting ticks.
module baud_gen #(
    parameter integer CLK_HZ = 50_000_000,
    parameter integer BAUD   = 115200,
    parameter integer OSR    = 16
)(
    input  wire clk,
    input  wire rst,
    output reg  tick
);
    localparam integer DIV = (CLK_HZ + (BAUD*OSR)/2) / (BAUD*OSR); // rounded
    localparam integer CW  = (DIV < 2) ? 1 : $clog2(DIV);
    reg [CW-1:0] cnt;
    always @(posedge clk) begin
        if (rst) begin
            cnt  <= {CW{1'b0}};
            tick <= 1'b0;
        end else if (cnt == DIV-1) begin
            cnt  <= {CW{1'b0}};
            tick <= 1'b1;
        end else begin
            cnt  <= cnt + 1'b1;
            tick <= 1'b0;
        end
    end
endmodule

// UART transmitter, 8-N-1. Idle line high. LSB first.
// Consumes 'tick' at BAUD*OSR; holds each bit for OSR ticks.
module uart_tx #(
    parameter integer OSR = 16
)(
    input  wire       clk,
    input  wire       rst,
    input  wire       tick,       // BAUD*OSR strobe
    input  wire       start,      // 1-clk pulse: latch data and begin
    input  wire [7:0] data,
    output reg        tx,         // serial output (idle high)
    output reg        busy
);
    localparam [1:0] IDLE=2'd0, START=2'd1, DATA=2'd2, STOP=2'd3;
    reg [1:0] state;
    reg [4:0] os;                 // 0..OSR-1
    reg [2:0] bidx;               // data bit index 0..7
    reg [7:0] sh;

    always @(posedge clk) begin
        if (rst) begin
            state<=IDLE; tx<=1'b1; busy<=1'b0; os<=0; bidx<=0; sh<=8'h00;
        end else begin
            case (state)
                IDLE: begin
                    tx<=1'b1; busy<=1'b0;
                    if (start) begin sh<=data; busy<=1'b1; os<=0; state<=START; end
                end
                START: begin
                    tx<=1'b0; busy<=1'b1;
                    if (tick) begin
                        if (os==OSR-1) begin os<=0; bidx<=0; state<=DATA; end
                        else os<=os+1'b1;
                    end
                end
                DATA: begin
                    tx<=sh[0];
                    if (tick) begin
                        if (os==OSR-1) begin
                            os<=0; sh<={1'b0, sh[7:1]};
                            if (bidx==3'd7) state<=STOP; else bidx<=bidx+1'b1;
                        end else os<=os+1'b1;
                    end
                end
                STOP: begin
                    tx<=1'b1;
                    if (tick) begin
                        if (os==OSR-1) begin os<=0; busy<=1'b0; state<=IDLE; end
                        else os<=os+1'b1;
                    end
                end
            endcase
        end
    end
endmodule

// UART receiver, 8-N-1, OSR-times oversampling. Idle line high, LSB first.
// Re-centers on the start bit, then samples each data bit at its center using
// a 3-sample majority vote for glitch rejection. Flags framing errors.
module uart_rx #(
    parameter integer OSR = 16
)(
    input  wire       clk,
    input  wire       rst,
    input  wire       tick,       // BAUD*OSR strobe
    input  wire       rx,         // serial input (idle high)
    output reg  [7:0] data,
    output reg        valid,      // 1-clk pulse when a byte is ready
    output reg        ferr        // framing error (stop bit not high)
);
    localparam [1:0] IDLE=2'd0, START=2'd1, DATA=2'd2, STOP=2'd3;
    reg [1:0] state;
    reg [4:0] os;
    reg [2:0] bidx;
    reg [7:0] sh;
    reg [1:0] vote;               // running sum of center samples

    // 2-flop synchronizer for the asynchronous serial input
    reg rx_m, rx_s;
    always @(posedge clk) begin rx_m<=rx; rx_s<=rx_m; end

    always @(posedge clk) begin
        if (rst) begin
            state<=IDLE; valid<=1'b0; ferr<=1'b0; os<=0; bidx<=0; sh<=8'h00; vote<=0;
        end else begin
            valid<=1'b0;
            case (state)
                IDLE: begin
                    if (tick && rx_s==1'b0) begin os<=0; state<=START; end
                end
                START: begin                       // confirm start at its center
                    if (tick) begin
                        if (os==OSR/2-1) begin
                            os<=0; bidx<=0;
                            state <= (rx_s==1'b0) ? DATA : IDLE;   // reject false start
                        end else os<=os+1'b1;
                    end
                end
                DATA: begin                        // sample bit center via 3-sample vote
                    if (tick) begin
                        if (os==OSR-3)      vote <= {1'b0, rx_s};
                        else if (os==OSR-2) vote <= vote + rx_s;
                        if (os==OSR-1) begin
                            os<=0;
                            sh <= { ((vote + rx_s) >= 2'd2) ? 1'b1 : 1'b0, sh[7:1] };
                            if (bidx==3'd7) state<=STOP; else bidx<=bidx+1'b1;
                        end else os<=os+1'b1;
                    end
                end
                STOP: begin
                    if (tick) begin
                        if (os==OSR-1) begin
                            os<=0; data<=sh; valid<=1'b1; ferr<=(rx_s==1'b0); state<=IDLE;
                        end else os<=os+1'b1;
                    end
                end
            endcase
        end
    end
endmodule

// Top-level convenience wrapper: one baud generator feeding a TX and RX,
// with TX serial looped straight into RX. Useful for board bring-up.
module uart_loopback #(
    parameter integer CLK_HZ = 50_000_000,
    parameter integer BAUD   = 115200,
    parameter integer OSR    = 16
)(
    input  wire       clk,
    input  wire       rst,
    input  wire       start,
    input  wire [7:0] tx_data,
    output wire       tx_busy,
    output wire [7:0] rx_data,
    output wire       rx_valid,
    output wire       rx_ferr,
    output wire       serial          // exposed loopback line
);
    wire tick, line;
    baud_gen #(CLK_HZ,BAUD,OSR) u_baud (.clk(clk),.rst(rst),.tick(tick));
    uart_tx  #(OSR) u_tx (.clk(clk),.rst(rst),.tick(tick),.start(start),
                          .data(tx_data),.tx(line),.busy(tx_busy));
    uart_rx  #(OSR) u_rx (.clk(clk),.rst(rst),.tick(tick),.rx(line),
                          .data(rx_data),.valid(rx_valid),.ferr(rx_ferr));
    assign serial = line;
endmodule
