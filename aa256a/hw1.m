close all
clear
clc
%% Problem 1

syms s11 s22 s33 s23 s13 s12 C S

sigma = [s11 s12 s13;
         s12 s22 s23;
         s13 s23 s33];

Rx = [1 0 0; 0 C S; 0 -S C];
sigma_x = Rx * sigma * Rx.';
disp("sigma_x:")
disp(simplify(sigma_x))

Ry = [C 0 -S; 0 1 0; S 0 C];
sigma_y = Ry * sigma * Ry.';
disp("sigma_y:")
disp(simplify(sigma_y))
