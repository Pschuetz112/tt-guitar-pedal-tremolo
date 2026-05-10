`default_nettype none

module tt_um_pschuetz_tremolo (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    // Inputs
    wire enable = ui_in[0];

    // Rate select
    wire [1:0] rate = ui_in[2:1];

    // Counter
    reg [23:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            counter <= 0;
        else
            counter <= counter + 1;
    end

    // Select different counter bits for speed
    wire tremolo;

assign tremolo =
    (rate == 2'b00) ? counter[4] :
    (rate == 2'b01) ? counter[5] :
    (rate == 2'b10) ? counter[6] :
                      counter[7];

assign uo_out[7:1] = counter[7:1];

    // Output
    assign uo_out[0] = enable ? tremolo : 1'b0;

    // Debug outputs
    assign uo_out[7:1] = counter[22:16];

    // Unused IOs
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    wire _unused = &{ena, uio_in};

endmodule
