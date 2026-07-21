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
