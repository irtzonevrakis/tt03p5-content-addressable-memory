// A simple associative array in verilog: Tinytapeout wrapper.
// // Copyright (C) 2023 Ioannis-Rafail Tzonevrakis.

module tt_um_cam(input  wire [7:0] ui_in,
                 output wire [7:0] uo_out,
                 input  wire [7:0] uio_in,
                 output wire [7:0] uio_out,
                 output wire [7:0] uio_oe,
                 input  wire       ena,
                 input  wire       clk,
                 input  wire       rst_n);
  
  assign uio_oe = 8'hff;
  
  cam cam0 (.clk(clk), .ena(ena), .rst_n(rst_n),
            .we(ui_in[7]), .content(ui_in[6:0]),
            .found_addr({uo_out, uio_out}));
endmodule
