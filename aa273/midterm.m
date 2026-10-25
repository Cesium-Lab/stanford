
clear all
clc
close all

T_N = [0.9 0.05 0.05; 0.05 0.9 0.05; 0.05 0.05 0.9];
T_F = [0.2 0.8 0; 0 0.2 0.8; 0.8 0 0.2];

y2_x = transpose([0.15 0.7 0.15]);
b0 = transpose([0.2 0.5 0.3]);
b1_pre = T_F * b0
b1 = y2_x .* b1_pre / sum(y2_x .* b1_pre)

b2_pre = T_N * b1
b2 = y2_x .* b2_pre / sum(y2_x .* b2_pre)

b3_pre = T_F * b2