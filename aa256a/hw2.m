clc
clear
close all
format short g

%% Problem 1

syms c s nu E

C_stress = E/(1 - nu^2) * [1 nu 0; nu 1 0; 0 0 (1-nu)/2];
T = [c*c s*s 2*c*s; s*s c*c -2*c*s; -s*c s*c c*c-s*s];
R = diag([1,1,2]);

C_prime_stress = T * C_stress * R / T / R;

diff_stress = C_stress - C_prime_stress;

disp("Plane stress C - C_prime diff:")
disp(simplify(diff_stress))


C_strain = E/(1 - nu^2) * [1 nu 0; nu 1 0; 0 0 (1-nu)/2];

C_prime_strain = T * C_strain * R / T / R;

diff_strain = C_strain - C_prime_strain;

disp("Plane strain C - C_prime diff:")
disp(simplify(diff_strain))

%% Problem 2

Ex = 23.2 * 1; % msi
Ey = 1.3 * 1; % msi
G = 0.90 * 1; % msi
nu_x = 0.28;
angle = deg2rad(20);

S = cast([1/Ex -nu_x/Ex 0; -nu_x/Ex, 1/Ey, 0; 0 0 1/G], "double");
T_20 = cast(subs(T, {c, s}, {cos(angle), sin(angle)}), 'double');
disp("S [1/MPa]:")
disp(S)
% fprintf(%X.Yf, S)
disp("T at 20º:")
disp(T_20)

S_bar = T_20' * S * T_20;

disp("S_bar_stress [1/MPa]:")
disp(S_bar)

E1 = 1/S_bar(1,1);
disp("E1 [MPa]:")
disp(E1)

nu_y = Ey / Ex * nu_x;
Q = cast([
    Ex/(1-nu_x*nu_y)      nu_x*Ey/(1-nu_x*nu_y) 0;
    nu_y*Ex/(1-nu_x*nu_y) Ey/(1-nu_x*nu_y) 0;
    0 0 G
    ], "double");
disp("Q [MPa]:")
disp(Q)

Q_bar = T_20 \ Q / T_20';

disp("Q_bar [MPa]:")
disp(Q_bar)

E1_star = Q_bar(1,1);
disp("E1_star [MPa]:")
disp(E1_star)