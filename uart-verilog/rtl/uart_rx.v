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
