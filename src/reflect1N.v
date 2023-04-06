`default_nettype none

// completely combinational
module reflect1N #(
  parameter MAX_BITS = 32,
  parameter MAX_BIT_COUNT = 5
)(
  input [MAX_BITS-1:0] value,
  input [MAX_BIT_COUNT-1:0] bitwidth,
  output reg [MAX_BITS-1:0] reflected_value
);

  wire [MAX_BITS-1:0] reflected;
  assign reflected = {
    value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7],
    value[8], value[9], value[10], value[11], value[12], value[13], value[14], value[15],
    value[16], value[17], value[18], value[19], value[20], value[21], value[22], value[23],
    value[24], value[25], value[26], value[27], value[28], value[29], value[30], value[31]
  };

  // should infer a large barrel shifter
  assign reflected_value = reflected >> (MAX_BITS - bitwidth - 1);
endmodule
