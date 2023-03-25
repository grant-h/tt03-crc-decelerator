`default_nettype none
`timescale 1ns/1ps

module crc_decelerator_tb(
    input [7:0] io_in,
    output [7:0] io_out
   );

    initial begin
        $dumpfile ("crc_decelerator_tb.vcd");
        $dumpvars (0, crc_decelerator_tb);
        #1;
    end

    wire clk, rst;
    wire [1:0] cmd;
    wire [3:0] data_in;

    // better names for tb
    assign clk = io_in[0];
    assign rst = io_in[1];
    assign cmd = io_in[3:2];
    assign data_in = io_in[7:4];

    // instantiate the DUT
    granth_crc_decelerator crc (
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif
        .io_in({data_in, cmd, rst, clk}),
        .io_out(io_out)
    );

endmodule
