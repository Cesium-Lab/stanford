clc
clear
close all
format short g

%% Problem 1

% Mpa
material.E1 = 152.1e3;
material.E2 = 8.5e3;
material.G = 4.2e3;
material.nu1 = 0.35;

% Mpa
material.Xt = 3500
material.Xc = 1540
material.Yt = 56
material.Yc = 150
material.S = 98

% mm
material.h = 0.127;

material.nu2 = material.E2 / material.E1 * material.nu1;
Q = [
    material.E1/(1-material.nu1*material.nu2)          material.nu1*material.E2/(1-material.nu1*material.nu2) 0;
    material.nu1*material.E2/(1-material.nu1*material.nu2) material.E2/(1-material.nu1*material.nu2)          0;
    0                                 0                                 material.G
    ];

T = @(x) [
    cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
    sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
    -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];


angles = [45 -45 90 0 60 -60 90 -60 60 0 90 -45 45];
num_layers = numel(angles);

[A,B,D,alpha,beta,delta] = laminate(Q, T, angles, material.h);

num_forces = 100;
N = linspace(0,1e5,num_forces);

% Criterion
failure_strain = zeros(num_forces,1);
for i = 1:num_forces
    eps0 = alpha * [0 0 N(i)]';
    ek = eps0;
    s_local = Q*ek;  % MPa
    
    for j = 1:num_layers
        Tk = T(deg2rad(angles(j)));
        Qbar_k = Tk \ Q / Tk';
        sig_xy = Qbar_k * eps0;
        sig_12 = Tk * sig_xy;
        % disp(sig_12)

        diff = (sig_12(1)/material.Xt)^2;
        disp(diff)
        % disp(material.Xt) 
    end
    disp(".")
end

%% Part 1a

% L1 = 12;  % in SUPPORT SPAN
% P1 = 100;  % lbf

% thickness_flange = numel(angles_flange) * material.h;  % in
% thickness_web = numel(angles_web) * material.h;  % in


% [A_w,B_w,D_w] = laminate(Q, T, angles_web, material.h);

% % Msi -> psi
% A11_f = 1e6 * A_f(1,1);   % lbf/in
% A11_w = 1e6 * A_w(1,1);   % lbf/in
% D11_f = 1e6 * D_f(1,1);   % lbf*in

% fprintf('\n==================== Part 1a ====================\n');
% fprintf('Flange A11 = %.3e lbf/in, D11 = %.3f lbf*in\n', A11_f, D11_f);
% fprintf('Web A11 = %.3e lbf/in\n\n', A11_w);

% disp("B = 0 because each laminate is symmetric about their respective midplanes")
% disp("So each ply's contributions is canceled out by the opposite one.")
% fprintf('Maximum B of flange = %.2e, and of web = %.2e (rounding error)\n', ...
%     max(abs(B_f(:))), max(abs(B_w(:))));

% %% Part 1b
% % Web and flange are both symmetric, so the neutral axis is at the mid-height
% t  = material.h;
% tf = thickness_flange;
% H  = height_web;
% mid_height = H + tf;                         % flange midplane to midplane



% q11 = @(a) 1e6 * getQ11(Q, T, a);
% P = [];
% % bottom flange
% for k = 1:3
%     P(end+1,:) = [(k-1)*t,       k*t,       w_flange, q11(0)];
% end   
% % web plies
% for a = angles_web
%     P(end+1,:) = [tf,     tf+H,      t,        q11(a)];
% end   
% % top flange
% for k = 1:3
%     P(end+1,:) = [tf+H+(k-1)*t,  tf+H+k*t,  w_flange, q11(0)];
% end   

% % size(P); % should be 10,4 sanity check

% % with individual plies
% z1 = P(:,1); z2 = P(:,2); b = P(:,3); E = P(:,4);
% z_NA = sum(E.*b.*(z2.^2-z1.^2)/2) / sum(E.*b.*(z2-z1));
% EI_p = sum(E.*b.*((z2-z_NA).^3-(z1-z_NA).^3)/3);

% % eq 2.41 in the book
% EI_flanges = 2 * (w_flange*D11_f + w_flange*(mid_height/2)^2*A11_f);
% EI_web = height_web^3/12 * A11_w;
% EI_eff = EI_flanges + EI_web;

% fprintf('\n==================== Part 1b ====================\n');
% fprintf('Neutral axis: z_NA = %.4f in from bottom (mid-depth = %.4f in)\n', z_NA, (2*tf+H)/2);
% fprintf('EI_flanges = %.4e lbf*in^2\n', EI_flanges);
% fprintf('EI_web = %.4e lbf*in^2\n', EI_web);
% fprintf('EI_eff = %.4e lbf*in^2\n', EI_eff);
% fprintf('EI ply-by-ply = %.4e, diff vs closed form = %.2e\n', EI_p, EI_p - EI_eff);

% %% Part 1c
% w_max = P1 * L1^3 / (48 * EI_eff);

% fprintf('\n==================== Part 1c ====================\n');
% fprintf('Midspan deflection w_max = %.6f in (downward)\n', w_max);

% %% Part2

% P2 = 400;
% L2 = 42;
% angles_t = [25 -25 -25 25];   % inside > outside
% n_t = numel(angles_t);

% % Q11bar of each ply (plane strain eq. 2.48)
% Q11 = zeros(1,n_t);
% for k = 1:n_t
%     % psi
%     Q11(k) = getQ11(Q, T, angles_t(k)) * 1e6;
% end



% a = @(x) 2 - x/L2;
% b2 = @(x) 3 - 2*x/L2;
% EI_tube = @(x) EI_section(x, a, b2, Q11, material.h);

% deflection_free_end = -integral(@(s) P2*(L2-s).^2 ./ arrayfun(EI_tube, s), 0, L2);

% fprintf('\n==================== Part 2 ====================\n');
% fprintf('Free-end deflection  = %.5f in\n', deflection_free_end);

%% Functions

function [A, B, D, alpha, beta, delta] = laminate(Q, T_func, angles, t_ply)
    n = numel(angles);
    z = linspace(-n*t_ply/2, n*t_ply/2, n+1);
    A = zeros(3); B = zeros(3); D = zeros(3);
    for k = 1:n
        Tk = T_func(deg2rad(angles(k)));
        Qbar = Tk \ Q / Tk';
        A = A + Qbar * (z(k+1) - z(k));
        B = B + Qbar * (z(k+1)^2 - z(k)^2) / 2;
        D = D + Qbar * (z(k+1)^3 - z(k)^3) / 3;
    end

    ABD = [A B; B' D];
    compliance = ABD \ eye(6);

    alpha = compliance(1:3,1:3);
    beta = compliance(1:3,4:6);
    delta = compliance(4:6,4:6);

end

% function EI = EI_section(x, a, b, Q11, t_ply)
%     n = numel(Q11);
    
%     EI = 0;
%     for k = 1:n
%         d_out = (n - k) * t_ply;     % depth of ply's outer face below outer surface
%         d_in = d_out + t_ply;
%         I_k = pi/4 * ((a(x)-d_out)^3 * (b(x)-d_out) - (a(x)-d_in)^3 * (b(x)-d_in));
%         EI = EI + Q11(k) * I_k;
%     end
% end

% function q11 = getQ11(Q, T, angle_deg)
% Tk = T(deg2rad(angle_deg));
% Qbar = Tk \ Q / Tk';
% q11 = Qbar(1,1);
% end
