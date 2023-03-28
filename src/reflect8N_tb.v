`default_nettype none
`timescale 1ns/1ps

module reflect8N_tb #(
  parameter MAX_BITS = 32,
  parameter MAX_BYTES = 4,
  parameter MAX_BYTE_WIDTH = 2
)(
    input [MAX_BITS-1:0] value,
    input [MAX_BYTE_WIDTH-1:0] bytewidth,
    output [MAX_BITS-1:0] reflected_value
   );

    initial begin
        $dumpfile ("reflect8N_tb.vcd");
        $dumpvars (0, reflect8N_tb);
        #1;
    end

    // instantiate the DUT
    reflect8N #(MAX_BITS, MAX_BYTES, MAX_BYTE_WIDTH) rf8N(
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif
        .value  (value),
        .bytewidth  (bytewidth),
        .reflected_value (reflected_value)
        );

endmodule
