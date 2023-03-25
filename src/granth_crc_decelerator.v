/*
 CRC Decelerator Top FSM

 RESET
  - No data. Resets CRC accumulator with CONFIG_INIT

 SETUP (variable cycle length):
   Cmd bitstring
     [config_lo - 4 bits] [config_hi - 4 bits] [poly X N-4B] [init X N-4B] [xor X N-4B]

   config_lo (4 bits) (MSB first)
     BIT_3: [width[3:0]] = data_in

   config_hi (4 bits) (MSB first)
     BIT_3: [width[5]] [width[4]] [reflect_out] [reflect_in]

   Output signal when setup complete

 MESSAGE
   [message_lo - 4 bits] [message_hi - 4 bits]
   Output current byte (with wrap around)

 FINAL
  - No data. Expect streamed CRC output on io_out
    Output current CRC byte
*/

`define BITWIDTH 64
`define BYTEWIDTH (`BITWIDTH/8)
`define NIBBLECOUNT (`BITWIDTH/4)

module granth_crc_decelerator (
  input [7:0] io_in,
  output reg [7:0] io_out
);
  wire clk, rst;
  wire [3:0] data_in;
  wire [1:0] cmd;

  // Friendly input names
  assign clk = io_in[0];
  assign rst = io_in[1];
  assign cmd = io_in[3:2];
  assign data_in = io_in[7:4];

  // Latched command and input data
  reg [1:0] current_cmd;
  reg [3:0] cur_data_in;

  // Top-level commands
  localparam
    CMD_RESET = 2'd0,
    CMD_SETUP = 2'd1,
    CMD_MESSAGE = 2'd2,
    CMD_FINAL = 2'd3;

  // CMD_SETUP FSM
  localparam
    SETUP_START = 3'd0,
    SETUP_CONFIG_LO = 3'd1,
    SETUP_CONFIG_HI = 3'd2,
    SETUP_POLY_N = 3'd3,
    SETUP_INIT_N = 3'd4,
    SETUP_XOR_N = 3'd5,
    SETUP_DONE = 3'd6;

  reg [2:0] setup_fsm;
  // Max nibbles is BITWIDTH/4
  reg [3:0] setup_nibble_count;

  // CRC primary parameters
  reg [5:0] bitwidth;
  wire [5-2:0] bitwidth_nibbles;
  reg crc_reflect_in, crc_reflect_out;
  reg [`BITWIDTH-1:0] crc_poly;
  reg [`BITWIDTH-1:0] crc_init;
  reg [`BITWIDTH-1:0] crc_xor;

  assign bitwidth_nibbles = bitwidth[5:2];

  wire setup_starting = current_cmd == CMD_SETUP && setup_fsm == SETUP_START;
  wire in_setup = (setup_fsm != SETUP_START && setup_fsm != SETUP_DONE) || setup_starting;

  // TODO: handle non-nibble aligned bitwidth
  wire bitwidth_reached = bitwidth_nibbles == (setup_nibble_count + 1);

  /////////////////////////////////
  // Common Registers and Logic
  /////////////////////////////////

  // Latch a copy of data from user input
  always @(posedge clk) begin
    if (rst)
      cur_data_in <= 4'b0;
    else
      cur_data_in <= data_in;
  end

  always @(*) begin
    case (current_cmd)
      CMD_SETUP: io_out = {7'b0, in_setup};
      default: io_out = 0;
    endcase
  end

  always @(posedge clk) begin
    if (rst)
      current_cmd <= CMD_RESET;
    else begin
      case (current_cmd)
      // hold CMD_SETUP while processing config stream
      CMD_SETUP: if (in_setup) current_cmd <= current_cmd; else current_cmd <= cmd;
      default: current_cmd <= cmd;
      endcase
    end
  end

  /////////////////////////////////
  // CMD_SETUP Registers and Logic
  /////////////////////////////////

  always @(posedge clk) begin
    if (rst) begin
      // A conservative default
      bitwidth <= 32;
      crc_reflect_in <= 0;
      crc_reflect_out <= 0;
    end else begin
      if (setup_fsm == SETUP_CONFIG_LO) begin
        bitwidth <= {bitwidth[5:4], cur_data_in};
        crc_reflect_in <= crc_reflect_in;
        crc_reflect_out <= crc_reflect_out;
      end else if (setup_fsm == SETUP_CONFIG_HI) begin
        bitwidth <= {cur_data_in[3:2], bitwidth[3:0]};
        crc_reflect_in <= cur_data_in[0];
        crc_reflect_out <= cur_data_in[1];
      end else begin
        bitwidth <= bitwidth;
        crc_reflect_in <= crc_reflect_in;
        crc_reflect_out <= crc_reflect_out;
      end
    end
  end

  always @(posedge clk) begin
    if (rst)
      setup_nibble_count <= 0;
    else begin
      if (setup_fsm == SETUP_POLY_N || setup_fsm == SETUP_INIT_N || setup_fsm == SETUP_XOR_N)
        if (bitwidth_reached)
          setup_nibble_count <= 0;
        else
          setup_nibble_count <= setup_nibble_count + 1;
      else
        setup_nibble_count <= 0;
    end
  end

  always @(posedge clk) begin
    if (rst)
      setup_fsm <= SETUP_START;
    else begin
      if (in_setup) begin
        case (setup_fsm)
          SETUP_START: setup_fsm <= SETUP_CONFIG_LO;
          SETUP_CONFIG_LO: setup_fsm <= SETUP_CONFIG_HI;
          SETUP_CONFIG_HI: setup_fsm <= SETUP_POLY_N;
          SETUP_POLY_N: if (bitwidth_reached) setup_fsm <= SETUP_INIT_N; else setup_fsm <= setup_fsm;
          SETUP_INIT_N: if (bitwidth_reached) setup_fsm <= SETUP_XOR_N; else setup_fsm <= setup_fsm;
          SETUP_XOR_N: if (bitwidth_reached) setup_fsm <= SETUP_DONE; else setup_fsm <= setup_fsm;
          SETUP_DONE: setup_fsm <= SETUP_START;
          default: setup_fsm <= SETUP_START;
        endcase
      end else begin
        setup_fsm <= SETUP_START;
      end
    end
  end

  genvar index;
  generate for (index = 0; index < `NIBBLECOUNT; index = index + 1) begin: assign_poly
    always @(posedge clk) begin
      if (rst | setup_starting) begin
        crc_poly <= `BITWIDTH'b0;
        crc_init <= `BITWIDTH'b0;
        crc_xor <= `BITWIDTH'b0;
      end else begin
        if (setup_fsm == SETUP_POLY_N) begin
          crc_poly[(index+1)*4-1:index*4] <= setup_nibble_count == index ? cur_data_in : crc_poly[(index+1)*4-1:index*4];
          crc_init <= crc_init;
          crc_xor <= crc_xor;
        end else if (setup_fsm == SETUP_INIT_N) begin
          crc_poly <= crc_poly;
          crc_init[(index+1)*4-1:index*4] <= setup_nibble_count == index ? cur_data_in : crc_init[(index+1)*4-1:index*4];
          crc_xor <= crc_xor;
        end else if (setup_fsm == SETUP_XOR_N) begin
          crc_poly <= crc_poly;
          crc_init <= crc_init;
          crc_xor[(index+1)*4-1:index*4] <= setup_nibble_count == index ? cur_data_in : crc_xor[(index+1)*4-1:index*4];
        end else begin
          crc_poly <= crc_poly;
          crc_init <= crc_init;
          crc_xor <= crc_xor;
        end
      end
    end
  end
  endgenerate

  /////////////////////////////////
  // CRC Datapath
  /////////////////////////////////

endmodule
