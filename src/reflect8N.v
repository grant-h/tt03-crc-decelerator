`default_nettype none

// completely combinational
module reflect8N #(
  parameter MAX_BITS = 32,
  parameter MAX_BYTES = 4,
  parameter MAX_BYTE_WIDTH = 2
)(
  input [MAX_BITS-1:0] value,
  input [MAX_BYTE_WIDTH-1:0] bytewidth, // max of 64-bits, 8 bytes, 0 -> 1 byte, 7 -> 8 bytes
  output reg [MAX_BITS-1:0] reflected_value
);
  // flipped bytes
  wire [7:0] fb [0:MAX_BYTES-1];

  // reflect all bytes individually
  genvar index;
  generate for (index = 0; index < MAX_BYTES; index = index + 1)
    begin: gencode
      reflect8 rf8 (
        .inp (value[((index+1)*8-1):index*8]),
        .outp (fb[index][7:0])
      );
    end
  endgenerate

  always @(*) begin
    case (bytewidth)
      0: reflected_value = {{MAX_BITS-8{1'b0}}, fb[0]};
      1: reflected_value = {{MAX_BITS-16{1'b0}}, fb[0], fb[1]};
      2: reflected_value = {{MAX_BITS-24{1'b0}}, fb[0], fb[1], fb[2]};
      3: reflected_value = {{MAX_BITS-32{1'b0}}, fb[0], fb[1], fb[2], fb[3]};
      /*4: reflected_value = {{MAX_BITS-40{1'b0}}, fb[0], fb[1], fb[2], fb[3], fb[4]};
      5: reflected_value = {{MAX_BITS-48{1'b0}}, fb[0], fb[1], fb[2], fb[3], fb[4], fb[5]};
      6: reflected_value = {{MAX_BITS-56{1'b0}}, fb[0], fb[1], fb[2], fb[3], fb[4], fb[5], fb[6]};
      7: reflected_value = {       fb[0], fb[1], fb[2], fb[3], fb[4], fb[5], fb[6], fb[7]};*/
      default:
         // never inferred
         reflected_value = 0;
    endcase
  end

endmodule
