clc
clear
close all
format short g

%% Problem 2
% Units: ksi and in throughout, so stresses are ksi and N is kip/in

% T800/3900-2
material.E1 = 23.2e3;
material.E2 = 1.30e3;
material.G = 0.90e3;
material.nu1 = 0.28;

material.Xt = 412;
material.Xc = 225;
material.Yt = 10;
material.Yc = 24.3;
material.S = 10;

material.h = 0.007;

% Vessel, plies listed inside to outside, 0 deg = vessel axis
angles = [0 60 -60 90 90 -60 60 0];
num_layers = numel(angles);
thickness = num_layers * material.h;  % in

D_outer = 20;       % in
L = 8 * 12;         % in

Q = getQ(material.E1, material.E2, material.G, material.nu1);

T = @(x) [
    cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
    sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
    -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];

% Each ply is an annulus, stepping inward from the outer surface
d_out = D_outer - 2 * (num_layers - (1:num_layers)) * material.h;
d_in = d_out - 2 * material.h;

[~,~,~,alpha,~,~,Qbar] = laminate(Q, T, angles, material.h);
Q11 = squeeze(Qbar(1,1,:))';
Q66 = squeeze(Qbar(3,3,:))';

%% Part a: bending rigidity
fprintf('\n==================== Part a ====================\n');
I = pi/64 * (d_out.^4 - d_in.^4);
EI = sum(Q11 .* I);  % kip*in^2
fprintf('EI = %.4e lbf*in^2\n', 1e3 * EI);

%% Part b: torsional rigidity
fprintf('\n==================== Part b ====================\n');
J = pi/32 * (d_out.^4 - d_in.^4);
GJ = sum(Q66 .* J);  % kip*in^2
fprintf('GJ = %.4e lbf*in^2\n', 1e3 * GJ);

%% Part c: Minimal pressure at which first ply failure occurs
fprintf('\n==================== Part c ====================\n');
R = (D_outer - thickness) / 2;  % mean radius

P = 0:0.1:10000;   % psi

N = [P*R/2; P*R; zeros(size(P))] / 1e3;   % kip/in
eps = alpha * N;

F1 = 1/material.Xt - 1/material.Xc;
F2 = 1/material.Yt - 1/material.Yc;
F11 = 1/(material.Xt*material.Xc);
F22 = 1/(material.Yt*material.Yc);
F66 = 1/material.S^2;
F12 = -0.5/sqrt(material.Xt*material.Xc*material.Yt*material.Yc);

p_fail = inf(1, num_layers);

for k = 1:num_layers
    s = Q / T(deg2rad(angles(k)))' * eps;   % ply axes, 3 x numel(P)
    FI = F1*s(1,:) + F2*s(2,:) + F11*s(1,:).^2 + F22*s(2,:).^2 + F66*s(3,:).^2 + 2*F12*s(1,:).*s(2,:);
    
    i_fail = find(FI >= 1, 1);
    if ~isempty(i_fail)
        p_fail(k) = P(i_fail);  % rip
    end
end

Pe = min(p_fail);
fprintf('Pe = %.1f psi\n', Pe);

%% Part d: maximum pressure with Yamada-Sun
fprintf('\n==================== Part d ====================\n');
small = 1e-6;
Q_YamSun = getQ(material.E1, small*material.E2, material.G, small*material.nu1);
[~,~,~,alpha_YamSun] = laminate(Q_YamSun, T, angles, material.h);
eps_YamSun = alpha_YamSun * N;

p_fail_ys = inf(1, num_layers);
for k = 1:num_layers
    s = Q_YamSun / T(deg2rad(angles(k)))' * eps_YamSun;
    X = material.Xt*(s(1,:) >= 0) + material.Xc*(s(1,:) < 0);
    FI = (s(1,:)./X).^2 + (s(3,:)/material.S).^2;
    i_fail = find(FI >= 1, 1);
    if ~isempty(i_fail)
        p_fail_ys(k) = P(i_fail);
    end
end
Pf = min(p_fail_ys);
fprintf('Pf = %.1f psi\n', Pf);

%% Part e: hole, point-stress criterion
fprintf('\n==================== Part e ====================\n');
d_hole = 2;         % in
d0 = 0.04;          % in, point-stress characteristic distance

% Hoop stress drives failure, so load direction is y (hoop) and the critical
% point is d0 from the hole edge along the vessel axis. Axial load is ignored,
% which is conservative.
Ex = 1/(thickness*alpha(1,1));
Ey = 1/(thickness*alpha(2,2));
Gxy = 1/(thickness*alpha(3,3));
nu_yx = -alpha(1,2)/alpha(2,2);

% Orthotropic stress concentration factor (infinite plate)
K_inf = 1 + sqrt(2*(sqrt(Ey/Ex) - nu_yx) + Ey/Gxy);

xi = (d_hole/2) / (d_hole/2 + d0);
stress_ratio = 1 + xi^2/2 + 3*xi^4/2 - (K_inf - 3)/2 * (5*xi^6 - 7*xi^8);

P_hole = Pf / stress_ratio;

fprintf('P with hole = %.1f psi\n', P_hole);

%% Functions (same as first problem)

function Q = getQ(E1, E2, G12, nu12)
    nu21 = E2 / E1 * nu12;
    Q = [
        E1/(1-nu12*nu21)      nu12*E2/(1-nu12*nu21) 0;
        nu12*E2/(1-nu12*nu21) E2/(1-nu12*nu21)      0;
        0                     0                     G12
        ];
end

function [A, B, D, alpha, beta, delta, Qbar] = laminate(Q, T_func, angles, t_ply)
    n = numel(angles);
    z = linspace(-n*t_ply/2, n*t_ply/2, n+1);
    A = zeros(3); B = zeros(3); D = zeros(3);
    Qbar = zeros(3, 3, n);  % one per ply
    for k = 1:n
        Tk = T_func(deg2rad(angles(k)));
        Qbar(:,:,k) = Tk \ Q / Tk';
        A = A + Qbar(:,:,k) * (z(k+1) - z(k));
        B = B + Qbar(:,:,k) * (z(k+1)^2 - z(k)^2) / 2;
        D = D + Qbar(:,:,k) * (z(k+1)^3 - z(k)^3) / 3;
    end

    ABD = [A B; B' D];
    compliance = ABD \ eye(6);

    alpha = compliance(1:3,1:3);
    beta = compliance(1:3,4:6);
    delta = compliance(4:6,4:6);
end
