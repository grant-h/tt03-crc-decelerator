`default_nettype none
`timescale 1ns/1ps

module reflect8_tb (
    // testbench is controlled by test.py
    input [7:0] inp,
    output [7:0] outp
   );

    // this part dumps the trace to a vcd file that can be viewed with GTKWave
    initial begin
        $dumpfile ("reflect8_tb.vcd");
        $dumpvars (0, reflect8_tb);
        #1;
    end

    // wire up the inputs and outputs

    // instantiate the DUT
    reflect8 rf8(
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif
        .inp  (inp),
        .outp (outp)
        );

endmodule

module reflect8N_tb (
    input [63:0] value,
    input [2:0] bytewidth,
    output [63:0] reflected_value
   );

    initial begin
        $dumpfile ("reflect8N_tb.vcd");
        $dumpvars (0, reflect8N_tb);
        #1;
    end

    // instantiate the DUT
    reflect8N rf8N(
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif
        .value  (value),
        .bytewidth  (bytewidth),
        .reflected_value (reflected_value)
        );

endmodule
