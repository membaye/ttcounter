## How it works

this is an 8-bit programmable binary counter with asynchronous reset, synchronous load, and tri-state outputs. the counter is a loop where the register holds the current count and the adder is always computing the count + 1, such that on every clock tick, the register grabs whichever value the muxes select. this loop when repeated millions of times a second is effectively, counting.

## How to test

first, set all ui_in inputs to 0 and press reset. uo_out should read 0. then set EN (ui_in[2]) high and run the clock slowly (a few Hz, or step it manually) so the count is visible. uo_out should count up. set EN low and the count should hold.

to load a value, keep OE (ui_in[1]) low so the uio pins are inputs. put a value on uio[7:0], then set LOAD (ui_in[0]) high for one clock edge. uo_out should show the loaded value.

to test the tri-state output, set OE high. the uio pins now drive the current count, matching uo_out. set OE low and they release.

to check the reset is asynchronous; while counting with the clock stopped, press reset. the count should clear immediately, without a clock edge.