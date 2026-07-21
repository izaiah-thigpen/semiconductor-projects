// Short DEMO testbench — sends a handful of bytes so the full waveform loads
// cleanly in EPWave. Use this one for a waveform screenshot.
// (Use the full testbench.sv for the 512-byte PASS/FAIL verification.)
`timescale 1ns/1ps
module tb_uart;
    localparam integer CLK_HZ = 16_000_000;
    localparam integer BAUD   = 1_000_000;   // DIV=1 -> fast sim
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

    integer errors = 0, checks = 0, k;
    reg [7:0] sent [0:7];
    integer wr = 0, rd = 0;

    always @(posedge clk) begin
        if (rx_valid) begin
            checks = checks + 1;
            if (rx_ferr || rx_data !== sent[rd]) begin
                $display("  MISMATCH #%0d: sent %02h got %02h ferr=%b", rd, sent[rd], rx_data, rx_ferr);
                errors = errors + 1;
            end else
                $display("  byte %0d OK: 0x%02h ('%s')", rd, rx_data, rx_data);
            rd = rd + 1;
        end
    end

    task send(input [7:0] b);
        begin
            @(negedge clk); sent[wr]=b; wr=wr+1; tx_data=b; start=1;
            @(negedge clk); start=0;
            wait (!tx_busy);
            repeat (OSR*3) @(posedge clk);
        end
    endtask

    initial begin
        $dumpfile("dump.vcd"); $dumpvars(0, tb_uart);
        repeat (8) @(posedge clk); rst=0;
        repeat (8) @(posedge clk);

        // spell "HI!" plus a couple of patterns — enough to see clearly
        send("H"); send("I"); send("!");
        send(8'hA5); send(8'h3C);

        repeat (OSR*6) @(posedge clk);
        $display("----------------------------------------");
        $display("DEMO: %0d bytes checked, %0d errors", checks, errors);
        $display(errors==0 ? "RESULT: PASS" : "RESULT: FAIL");
        $display("----------------------------------------");
        $finish;
    end
endmodule
