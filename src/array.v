// A simple associative array in verilog: Main array logic.
// Copyright (C) 2023 Ioannis-Rafail Tzonevrakis.

module cam(input wire clk, ena, rst_n, we,
           input wire [6:0] content,
           output reg [15:0] found_addr);
  reg [6:0] data [15:0]; // data registers
  reg [3:0] current_address;

  always @(posedge clk) begin
    if (!rst_n)
      current_address <= 4'd0;
    else begin
      if (we) begin
        // Register write logic
        data[current_address] <= content;
	// 16 registers (max address 4'd15) fit nicely
        current_address <= current_address + 1;
      end
    end
  end
  
  // Register file generation
  genvar i;
  generate
    for (i = 0;i < 16;i = i+1) begin
      always @(posedge clk) begin
          if (!rst_n) begin //Reset logic
            data[i] <= 7'd0;
            found_addr[i] <= 'd0;
          end
          else begin // Matching logic
            if (data[i] == content)
              found_addr[i] <= 'd1;
            else
              found_addr[i] <= 'd0;
          end
        end
    end
  endgenerate



endmodule
