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
