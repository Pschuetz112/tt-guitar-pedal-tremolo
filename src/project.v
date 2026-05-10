``default_nettype none

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
    wire [1:0] rate  = ui_in[2:1];
    wire [1:0] depth = ui_in[4:3];

    // Slow LFO counter and fast PWM counter
    reg [7:0] lfo_counter;
    reg [7:0] pwm_counter;
    reg [7:0] rate_divider;

    wire [7:0] rate_limit;

    assign rate_limit =
        (rate == 2'b00) ? 8'd4  :
        (rate == 2'b01) ? 8'd8  :
        (rate == 2'b10) ? 8'd16 :
                          8'd32;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            lfo_counter  <= 8'd0;
            pwm_counter  <= 8'd0;
            rate_divider <= 8'd0;
        end else begin
            pwm_counter <= pwm_counter + 8'd1;

            if (rate_divider >= rate_limit) begin
                rate_divider <= 8'd0;
                lfo_counter  <= lfo_counter + 8'd1;
            end else begin
                rate_divider <= rate_divider + 8'd1;
            end
        end
    end

    // Depth control:
    // depth 00 = light modulation
    // depth 11 = deepest modulation
    wire [7:0] min_level;

    assign min_level =
        (depth == 2'b00) ? 8'd192 :
        (depth == 2'b01) ? 8'd128 :
        (depth == 2'b10) ? 8'd64  :
                           8'd0;

    wire [7:0] modulation_level;

    assign modulation_level = min_level + {2'b00, lfo_counter[7:2]};

    wire pwm_out;

    assign pwm_out = enable ? (pwm_counter < modulation_level) : 1'b0;

    // Main output
    assign uo_out[0] = pwm_out;

    // Debug outputs
    assign uo_out[1] = lfo_counter[7];
    assign uo_out[2] = pwm_counter[7];
    assign uo_out[3] = enable;
    assign uo_out[7:4] = modulation_level[7:4];

    // Unused bidirectional IOs
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    wire _unused = &{ena, uio_in, ui_in[7:5], 1'b0};

endmodule
