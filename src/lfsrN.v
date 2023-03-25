`default_nettype none

module lfsrN #(
  parameter N = 8
)(
  input clk,
  input rst,
  input load,
  input shift,
  input data,
  input [N-1:0] taps,
  input [N-1:0] init_value,
  output reg [N-1:0] value
);

  wire [1:0] cmd;
  wire msb;

  assign cmd = {load, shift};
  assign msb = value[N-1];

  wire [N-1:0] value_shifted;
  assign value_shifted = {value[N-2:0], 1'b0};

  always @(posedge clk) begin
    if (rst) begin
      value <= 0;
    end else begin

      // One-hot command. Hold value otherwise for illegal configuration
      case (cmd)
        // CMD_SHIFT
        2'b01: value[N-1:0] <= (msb ^ data) ? {value_shifted[N-1:1] ^ taps[N-1:1], 1'b1} : value_shifted;
        // CMD_LOAD
        2'b10: value <= init_value;
        // CMD_HOLD (0 or 3)
        default: value <= value;
      endcase
    end
  end

endmodule
