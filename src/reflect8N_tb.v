`default_nettype none
`timescale 1ns/1ps

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
