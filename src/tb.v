// A simple associative array in verilog: Testbench harness for cocotb.
// Copyright (C) 2023 Ioannis-Rafail Tzonevrakis.

`default_nettype none
`timescale 1ns/1ps

module tb(input wire clk, rst_n, we,
          input wire [6:0] content,
          output wire [15:0] found_addr);

  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, tb);
    #1;
  end

  wire [7:0] ui_in, uo_out, uio_in, uio_out, uio_oe;
  wire ena;

  assign ena = 1;

  assign ui_in[7] = we;
  assign ui_in[6:0] = content;
  assign found_addr = {uo_out, uio_out};

  tt_um_cam dut0 (.ui_in(ui_in), .uo_out(uo_out), .uio_in(uio_in),
                  .uio_out(uio_out), .uio_oe(uio_oe), .ena(ena),
                  .clk(clk), .rst_n(rst_n),
                  `ifdef GL_TEST
                    // Power pins for gate-level test
                    .vccd1( 1'b1),
                    .vssd1( 1'b0)
                  `endif
                 );
endmodule
