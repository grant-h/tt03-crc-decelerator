`default_nettype none

module reflect8 (
  input [7:0] inp,
  output [7:0] outp
);

  assign outp = {
    inp[0], inp[1], inp[2], inp[3],
    inp[4], inp[5], inp[6], inp[7]
  };

endmodule
