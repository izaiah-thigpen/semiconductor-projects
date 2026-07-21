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
