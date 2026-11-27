clc
clear
close all
format short g

%% Problem 1
% Units: MPa and mm throughout, so stresses are MPa and N is N/mm


material.E1 = 152.1e3;
material.E2 = 8.5e3;
material.G = 4.2e3;
material.nu1 = 0.35;

material.Xt = 3500;
material.Xc = 1540;
material.Yt = 56;
material.Yc = 150;
material.S = 98;

material.h = 0.127;

Q = getQ(material.E1, material.E2, material.G, material.nu1);

T = @(x) [
    cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
    sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
    -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];

angles = [45 -45 90 0 60 -60 90 -60 60 0 90 -45 45];
num_layers = numel(angles);
thickness = num_layers * material.h;  % mm, laminate thickness

% small factor instead of 0 so ABD stays invertible
small = 1e-6;
Q_matrix_failed = getQ(material.E1, small*material.E2, small*material.G, small*material.nu1);
Q_fiber_failed = small * Q;

% Tracking which ones fail
% 0 = intact, 1 = matrix failed, 2 = fiber failed
ply_state = zeros(num_layers, 1);
Q_ply = repmat(Q, 1, 1, num_layers);

[A,B,D,alpha,beta,delta] = laminate(Q_ply, T, angles, material.h);

num_forces = 500;
N = linspace(0, 1400, num_forces);  % Trying to get it to 16000 microstrain

% Results
eps_x = zeros(num_forces, 1);    % laminate axial strain
sigma_x = N' / thickness;                % MPa, laminate axial stress
last = num_forces;
for i = 1:num_forces


    % Keep re-checking at this load until no new ply fails
    failed = true;
    while failed
        failed = false;
        [~,~,~,alpha] = laminate(Q_ply, T, angles, material.h);
        eps0 = alpha * [N(i) 0 0]';

        for j = 1:num_layers
            Tk = T(deg2rad(angles(j)));
            Qbar_k = Tk \ Q_ply(:,:,j) / Tk';
            sig_12 = Tk * Qbar_k * eps0;
            [diff_fiber, diff_matrix] = hashin(sig_12, material);

            if diff_fiber >= 1 && ply_state(j) < 2
                ply_state(j) = 2;
                Q_ply(:,:,j) = Q_fiber_failed;
                failed = true;
                fprintf('Ply %2d (%3d deg) fiber failure  at %.1f MPa\n', j, angles(j), sigma_x(i));
            elseif diff_matrix >= 1 && ply_state(j) < 1
                ply_state(j) = 1;
                Q_ply(:,:,j) = Q_matrix_failed;
                failed = true;
                fprintf('Ply %2d (%3d deg) matrix failure at %.1f MPa\n', j, angles(j), sigma_x(i));
            end
        end
    end

    % Laminate is gone once the 0 deg plies break or it goes crazy 
    if all(ply_state(angles == 0) == 2)
        last = i - 1;
        fprintf('Final failure at sigma = %.1f MPa\n', sigma_x(i));
        break
    end

    eps_x(i) = eps0(1);
end

% Approximate paper values from graph
fig4 = [
    0 0; 
    3000 110; 
    5000 210;
    8000 280;
    12000 400;
    16000 540];

figure
plot(1e6*eps_x(1:last), sigma_x(1:last), 'LineWidth', 1.5)
hold on
plot(1e6*[eps_x(last) eps_x(last)], [sigma_x(last) 0], 'b--')  % final failure
plot(fig4(:,1), fig4(:,2), 'k-o')
xlim([0 max(16000, 1.05e6*eps_x(last))])
xlabel('Axial strain (\mu\epsilon)')
ylabel('Axial stress (MPa)')
legend('Hashin progressive failure', 'Final failure', 'McManus & Mak Fig. 4 prediction', 'Location', 'northwest')
grid on

%% Functions

% in ply axes (MPa)
function [diff_fiber, diff_matrix] = hashin(sig_xy, m)
    sx = sig_xy(1); sy = sig_xy(2); sxy = sig_xy(3);

    if sx >= 0
        diff_fiber = (sx/m.Xt)^2 + (sxy/m.S)^2;
    else
        diff_fiber = (sx/m.Xc)^2;
    end

    if sy >= 0
        diff_matrix = (sy/m.Yt)^2 + (sxy/m.S)^2;
    else
        diff_matrix = (sy/(2*m.S))^2 + ((m.Yc/(2*m.S))^2 - 1)*sy/m.Yc + (sxy/m.S)^2;
    end
end

function Q = getQ(E1, E2, G12, nu12)
    nu21 = E2 / E1 * nu12;
    Q = [
        E1/(1-nu12*nu21)      nu12*E2/(1-nu12*nu21) 0;
        nu12*E2/(1-nu12*nu21) E2/(1-nu12*nu21)      0;
        0                     0                     G12
        ];
end

% Q is either a single for all ply, or individually for each ply
function [A, B, D, alpha, beta, delta] = laminate(Q, T_func, angles, t_ply)
    n = numel(angles);
    if size(Q, 3) == 1
        Q = repmat(Q, 1, 1, n);
    end
    z = linspace(-n*t_ply/2, n*t_ply/2, n+1);
    A = zeros(3); B = zeros(3); D = zeros(3);
    for k = 1:n
        Tk = T_func(deg2rad(angles(k)));
        Qbar = Tk \ Q(:,:,k) / Tk';
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