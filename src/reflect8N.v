`default_nettype none

// completely combinational
module reflect8N (
  input [63:0] value,
  input [2:0] bytewidth, // max of 64-bits, 8 bytes, 0 -> 1 byte, 7 -> 8 bytes
  output reg [63:0] reflected_value
);
  // flipped bytes
  wire [7:0] fb [0:7];

  // reflect all bytes individually
  genvar index;
  generate for (index = 0; index < 8; index = index + 1)
    begin: gencode
      reflect8 rf8 (
        .inp (value[((index+1)*8-1):index*8]),
        .outp (fb[index][7:0])
      );
    end
  endgenerate

  always @(*) begin
    case (bytewidth)
      0: reflected_value = {56'b0, fb[0]};
      1: reflected_value = {48'b0, fb[0], fb[1]};
      2: reflected_value = {36'b0, fb[0], fb[1], fb[2]};
      3: reflected_value = {32'b0, fb[0], fb[1], fb[2], fb[3]};
      4: reflected_value = {24'b0, fb[0], fb[1], fb[2], fb[3], fb[4]};
      5: reflected_value = {16'b0, fb[0], fb[1], fb[2], fb[3], fb[4], fb[5]};
      6: reflected_value = {8'b0 , fb[0], fb[1], fb[2], fb[3], fb[4], fb[5], fb[6]};
      7: reflected_value = {       fb[0], fb[1], fb[2], fb[3], fb[4], fb[5], fb[6], fb[7]};
      default:
         // never inferred
         reflected_value = {64'b0};
    endcase
  end

endmodule
