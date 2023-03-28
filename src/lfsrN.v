`default_nettype none

module lfsrN #(
  parameter MAX_BITS = 64,
  parameter MAX_BIT_COUNT = 6
)(
  input clk,
  input rst,
  input load,
  input shift,
  input data,
  input [MAX_BIT_COUNT-1:0] bitwidth, // TODO: use LOG2 macro
  input [MAX_BITS-1:0] taps,
  input [MAX_BITS-1:0] init_value,
  output reg [MAX_BITS-1:0] value
);

  wire [1:0] cmd;
  wire msb;

  assign cmd = {load, shift};
  assign msb = value[bitwidth];

  wire [MAX_BITS-1:0] value_shifted;
  assign value_shifted = {value[MAX_BITS-2:0], 1'b0};

  always @(posedge clk) begin
    if (rst) begin
      value <= 0;
    end else begin

      // One-hot command. Hold value otherwise for illegal configuration
      case (cmd)
        // CMD_SHIFT
        2'b01: value[MAX_BITS-1:0] <= (msb ^ data) ? value_shifted[MAX_BITS-1:0] ^ taps[MAX_BITS-1:0] : value_shifted;
        // CMD_LOAD
        2'b10: value <= init_value;
        // CMD_HOLD (0 or 3)
        default: value <= value;
      endcase
    end
  end

endmodule
