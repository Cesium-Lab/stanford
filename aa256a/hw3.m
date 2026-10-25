clc
clear
close all
format short g

%% Problem 1

Ex = 23.2; % Msi
Ey = 1.3; % Msi
G = 0.90; % Msi
nu_x = 0.28;

h = 0.007; % in

nu_y = Ey / Ex * nu_x;

Q = cast([
    Ex/(1-nu_x*nu_y)      nu_x*Ey/(1-nu_x*nu_y) 0;
    nu_y*Ex/(1-nu_x*nu_y) Ey/(1-nu_x*nu_y) 0;
    0 0 G
    ], "double");

T = @(x) [
    cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
    sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
    -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];

angles = [
    0 0 90 90;
    30 -30 -30 30;
    45 -45 -45 45;
    0 60 60 0;
    0 45 -45 90
    ];

[N, N_layers] = size(angles);

[As,Bs,Ds,alphas,betas,deltas] = laminate_matrices(Q, angles, T, h);

names = {'A', 'B', 'D', 'alpha', 'beta', 'delta'};
units = {'Msi•in', 'Msi•in^2', 'Msi•in^3', '1/(Msi•in)', '1/(Msi•in^2)', '1/(Msi•in^3)'};
matrices = {As, Bs, Ds, alphas, betas, deltas};

fprintf('\n==================== Problem 1 ====================\n');
for i = 1:N
    fprintf('\n==================== Specimen %d ====================\n', i);

    for j = 1:length(matrices)
        fprintf('\n%s [%s]:\n', names{j}, units{j});
        disp(matrices{j}(:,:,i));
    end
end



%% Problem 2
angles2 = angles - 15;
[As2,Bs2,Ds2,alphas2,betas2,deltas2] = laminate_matrices(Q, angles2, T, h);
names = {'A', 'B', 'D', 'alpha', 'beta', 'delta'};
matrices = {As2, Bs2, Ds2, alphas2, betas2, deltas2};

fprintf('\n==================== Problem 2 ====================\n');
fprintf('\n===== Sufficiently long specimen =====\n\n');

alpha11 = squeeze(alphas2(1,1,:));
E11 = 1 ./ (alpha11 * h * N_layers);

fprintf('\nEffective Tensile Modulus E11:\n');

for i = 1:N
    fprintf('Specimen %d: %.4f Msi\n', i, E11(i));
end


