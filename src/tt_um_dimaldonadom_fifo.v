`default_nettype none

module tt_um_dimaldonadom_fifo(
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    // TinyTapeout input mapping:
    // ui_in[7:0]  -> FIFO data input
    // uio_in[0]   -> write enable
    // uio_in[1]   -> read enable
    //
    // TinyTapeout output mapping:
    // uo_out[7:0] -> FIFO data output
    // uio_out[2]  -> full flag
    // uio_out[3]  -> empty flag

    wire wr_en_i;
    wire rd_en_i;
    wire full_o;
    wire empty_o;
    wire rst;

    assign wr_en_i = uio_in[0];
    assign rd_en_i = uio_in[1];
    assign rst = ~rst_n;

    fifo #(
        .WIDTH(8),
        .DEPTH(16)
    ) fifo_inst (
        .clk(clk),
        .rst(rst),
        .wr_en(wr_en_i),
        .d_in(ui_in),
        .rd_en(rd_en_i),
        .d_out(uo_out),
        .full(full_o),
        .empty(empty_o)
    );

    assign uio_out[0] = 1'b0;
    assign uio_out[1] = 1'b0;
    assign uio_out[2] = full_o;
    assign uio_out[3] = empty_o;
    assign uio_out[4] = 1'b0;
    assign uio_out[5] = 1'b0;
    assign uio_out[6] = 1'b0;
    assign uio_out[7] = 1'b0;

    // uio[0] and uio[1] are inputs.
    // uio[2] and uio[3] are outputs for full/empty.
    // The rest are unused inputs.
    assign uio_oe = 8'b0000_1100;

    // Avoid unused warning for ena.
    wire _unused = &{ena, uio_in[7:2], 1'b0};

endmodule

`default_nettype wire
