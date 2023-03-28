`default_nettype none
`timescale 1ns/1ps

module lfsrN_tb #(
  parameter WIDTH = 32,
  parameter BIT_COUNT = 5
)(
    input clk,
    input rst,
    input load,
    input shift,
    input data,
    input [BIT_COUNT-1:0] bitwidth,
    input [WIDTH-1:0] taps,
    input [WIDTH-1:0] init_value,
    output [WIDTH-1:0] value
   );

    initial begin
        $dumpfile ("lfsrN_tb.vcd");
        $dumpvars (0, lfsrN_tb);
        #1;
    end

    // instantiate the DUT
    lfsrN #(WIDTH, BIT_COUNT) lfsr (
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif
        clk,
        rst,
        load,
        shift,
        data,
        bitwidth,
        taps,
        init_value,
        value
    );

endmodule
