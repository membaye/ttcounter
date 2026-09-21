/*
 * Copyright (c) 2026 Matthew Embaye
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_counter (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

  wire load = ui_in[0];
  wire oe   = ui_in[1];
  wire en   = ui_in[2];

  reg [7:0] count;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      count <= 8'd0;
    else if (load)
      count <= uio_in;
    else if (en)
      count <= count + 8'd1;
  end

  assign uo_out  = count;
  assign uio_out = count;
  assign uio_oe  = {8{oe}};

  wire _unused = &{ena, ui_in[7:3], 1'b0};

endmodule
