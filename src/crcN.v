module crcN #(
  parameter MAX_BITS = 64
)(
  input clk,
  input rst,
  input initialize,
  input shift,
  input reflect_in,
  input reflect_out,
  input [5:0] bitwidth,
  input [7:0] data,
  input [2:0] bit_index,
  input [MAX_BITS-1:0] poly,
  input [MAX_BITS-1:0] init_value,
  input [MAX_BITS-1:0] xor_out,
  output [MAX_BITS-1:0] crc
);
  wire [MAX_BITS-1:0] crc_lfsr;
  wire [MAX_BITS-1:0] crc_reflected;

  assign crc = (reflect_out ? crc_reflected : crc_lfsr) ^ xor_out;

  wire [7:0] data_reflected;
  wire current_bit = reflect_in ? data_reflected[bit_index] : data[bit_index];

  reflect8 ref8 ( .inp(data), .outp(data_reflected));

  reflect8N refout (
    .value (crc_lfsr),
    .bytewidth (bitwidth[5:3]),
    .reflected_value (crc_reflected)
  );

  lfsrN #(MAX_BITS) lfsr (
    .clk (clk),
    .rst (rst),
    .load (initialize),
    .shift (shift),
    .data (current_bit),
    .bitwidth (bitwidth),
    .taps (poly),
    .init_value (init_value),
    .value (crc_lfsr)
  );

endmodule
