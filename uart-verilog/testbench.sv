// Self-checking testbench: drives bytes through TX, loops the serial line into
// RX, and checks every received byte against what was sent. Reports PASS/FAIL
// and dumps a VCD for waveform viewing.
`timescale 1ns/1ps
module tb_uart;
    localparam integer CLK_HZ = 16_000_000;
    localparam integer BAUD   = 1_000_000;   // DIV=1 -> fast simulation
    localparam integer OSR    = 16;

    reg clk=0, rst=1, start=0;
    reg  [7:0] tx_data;
    wire [7:0] rx_data;
    wire tx_busy, rx_valid, rx_ferr, serial;

    uart_loopback #(CLK_HZ,BAUD,OSR) dut (
        .clk(clk),.rst(rst),.start(start),.tx_data(tx_data),
        .tx_busy(tx_busy),.rx_data(rx_data),.rx_valid(rx_valid),
        .rx_ferr(rx_ferr),.serial(serial));

    always #31.25 clk = ~clk;                 // 16 MHz

    integer errors = 0, checks = 0, i;
    reg [7:0] sent [0:511];
    integer wr = 0, rd = 0;

    // capture received bytes and compare in-order
    always @(posedge clk) begin
        if (rx_valid) begin
            checks = checks + 1;
            if (rx_ferr) begin
                $display("  FRAME ERROR on byte %0d", rd);
                errors = errors + 1;
            end else if (rx_data !== sent[rd]) begin
                $display("  MISMATCH #%0d: sent %02h got %02h", rd, sent[rd], rx_data);
                errors = errors + 1;
            end
            rd = rd + 1;
        end
    end

    task send(input [7:0] b);
        begin
            @(negedge clk); sent[wr]=b; wr=wr+1; tx_data=b; start=1;
            @(negedge clk); start=0;
            wait (!tx_busy);                  // wait for frame to finish
            repeat (OSR*4) @(posedge clk);    // stop-bit + settle
        end
    endtask

    initial begin
        $dumpfile("dump.vcd"); $dumpvars(0, tb_uart);
        repeat (8) @(posedge clk); rst=0;
        repeat (8) @(posedge clk);

        // 1) all 256 byte values
        for (i=0; i<256; i=i+1) send(i[7:0]);
        // 2) a batch of pseudo-random bytes
        for (i=0; i<256; i=i+1) send($random);

        repeat (OSR*8) @(posedge clk);
        $display("--------------------------------------------------");
        $display("UART loopback: %0d bytes checked, %0d errors", checks, errors);
        $display(errors==0 ? "RESULT: PASS" : "RESULT: FAIL");
        $display("--------------------------------------------------");
        $finish;
    end
endmodule
