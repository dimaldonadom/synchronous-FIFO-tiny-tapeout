//////////////////////////////////////////////////////////////////////////////////
// Institution: Ecole de mines de Saint-Etienne
// Engineer: Diego Alejandro Maldonado Marin
// 
// Create Date: 22.04.2026
// Design Name: symetric fifo
// Module Name: fifo
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: Esta memoria esta pensada para que la profundidad sea potencia de 2,
// de esta manera no es necesario comparar los punteros para saber cuando reiniciar.
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 8
)(
    // Inputs
    input wire clk,
    input wire rst,
    input wire wr_en,
    input wire rd_en,
    input wire [WIDTH-1:0] d_in,
    // Outputs
    output wire [WIDTH-1:0] d_out,
    output reg full,
    output reg empty
);

parameter AW = $clog2(DEPTH);

reg [DEPTH-1:0][WIDTH-1:0] MEM;

reg [AW:0] wr_ptr_q, wr_ptr_n;
reg [AW:0] rd_ptr_q, rd_ptr_n;

reg [WIDTH-1:0] d_out_q, d_out_n;

// DFF - d_out 
always @(posedge clk or posedge rst) begin
    if (rst) begin
        d_out_q <= 0;
    end else begin
        d_out_q <= d_out_n;
    end
end

// DFF - MEM 
always @(posedge clk or posedge rst) begin
    if (rst) begin
        MEM <= 0;
    end else if(wr_en && !full && !(rd_en && empty)) begin
        MEM[wr_ptr_q[AW-1:0]] <= d_in;
    end
end

// DFF - wr_ptr and rd_ptr
always @(posedge clk or posedge rst) begin
    if (rst) begin
        wr_ptr_q <= 0;
        rd_ptr_q <= 0;
    end else begin
        wr_ptr_q <= wr_ptr_n;
        rd_ptr_q <= rd_ptr_n;
    end
end

always @(*) begin
    // Write
    if(wr_en && !full && !(rd_en && empty)) begin
        wr_ptr_n = wr_ptr_q + 1'b1;
    end 
    else begin
        wr_ptr_n = wr_ptr_q;
    end

    // Read
    if(rd_en && !empty) begin
        rd_ptr_n = rd_ptr_q + 1'b1;
    end 
    else begin
        rd_ptr_n = rd_ptr_q;
    end

    // Output
    if (rd_en && wr_en && empty) begin
        d_out_n = d_in;
    end
    else if(rd_en && !empty) begin
        d_out_n = MEM[rd_ptr_q[AW-1:0]];
    end 
    else begin
        d_out_n = d_out_q;
    end
end

always @(*) begin
    full = ((wr_ptr_q[AW-1:0]==rd_ptr_q[AW-1:0]) && (wr_ptr_q[AW]!=rd_ptr_q[AW]));
    empty = wr_ptr_q == rd_ptr_q;
end

assign d_out = d_out_q;

endmodule