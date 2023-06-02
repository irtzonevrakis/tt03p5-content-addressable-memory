// A simple associative array in verilog: Main array logic.
// Copyright (C) 2023 Ioannis-Rafail Tzonevrakis.

module cam(input wire clk, ena, rst_n, we,
           input wire [6:0] content,
           output reg [15:0] found_addr);
  wire [6:0] data [15:0]; // data registers
  reg [15:0] current_address;

  always @(posedge clk) begin
    if (!rst_n) begin
      current_address <= 4'd1;
      found_addr <= 16'd0;
    end
    else begin
      if (we) begin
        // 16 registers (max address 4'd15) fit nicely
        if (current_address == 16'h8000)
          current_address <= 16'd1;
        else
          current_address <= current_address << 1;
      end
    end
  end
  
  // Register file generation
  genvar i;
  generate
    for (i = 0;i < 16;i = i+1) begin
      memory_element ele (.clk(clk),
                          .rst_n(rst_n),
                          .we(we & current_address[i]),
                          .d(content),
                          .q(data[i])
                         );
      always @(posedge clk) begin
          if (rst_n) begin // Matching logic
            if (data[i] == content)
              found_addr[i] <= 'd1;
            else
              found_addr[i] <= 'd0;
          end
        end
    end
  endgenerate
  
endmodule

module memory_element(input clk, rst_n, we,
                      input [6:0] d,
                      output reg [6:0] q);
  always @(posedge clk) begin
    if (!rst_n) begin
      q <= 7'd0;
    end
    else begin
      if (we)
        q <= d;
    end
  end
endmodule
