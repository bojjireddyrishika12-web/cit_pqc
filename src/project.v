/*
 * project.v - 8-Bit NTT-Based PQC Core
 */
`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // 8-bit input data
    output wire [7:0] uo_out,   // 8-bit NTT output
    input  wire [7:0] uio_in,   // Bidirectional inputs (unused)
    output wire [7:0] uio_out,  // Status outputs
    output wire [7:0] uio_oe,   // Output enables
    input  wire       ena,      // Enable
    input  wire       clk,      // Clock
    input  wire       rst_n     // Active-low reset
);

    // NTT Parameters: prime q=17, primitive root w=3
    // For 8-bit demo: single butterfly unit
    // Output = (input * w) mod q
    // w=3, q=17

    reg [7:0] ntt_out;
    reg ready_flag;
    reg done_flag;

    // NTT Butterfly: y = (x * 3) mod 17
    function [7:0] ntt_butterfly;
        input [7:0] x;
        reg [15:0] product;
        begin
            product = x * 8'd3;
            ntt_butterfly = product % 8'd17;
        end
    endfunction

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ntt_out    <= 8'h00;
            ready_flag <= 1'b0;
            done_flag  <= 1'b0;
        end else begin
            ready_flag <= 1'b1;
            ntt_out    <= ntt_butterfly(ui_in);
            done_flag  <= 1'b1;
        end
    end

    assign uo_out  = ntt_out;
    assign uio_out = {6'b0, done_flag, ready_flag};
    assign uio_oe  = 8'b0000_0011;

    wire _unused = &{ena, uio_in, 1'b0};

endmodule
