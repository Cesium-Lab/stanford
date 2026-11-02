clc
clear
close all
format short g

%% Materials

% Q1: T800/3900-2

% Msi
Q1.Ex = 23.2;          
Q1.Ey = 1.30;          
Q1.G = 0.90;     
      
Q1.nu_x = 0.28;

% 1/deg F
Q1.alpha_x = -6.8e-6;   
Q1.alpha_y = 32e-6;     
% in
Q1.h = 0.007;

% ksi
Q1.Xt = 412;           
Q1.Xc = 225;           
Q1.Yt = 10;            
Q1.Yc = 24.3;          
Q1.S = 10;             

% Q2: T800SC/3900-2B

% Msi
Q2.Ex = 21.5;          
Q2.Ey = 1.20;          
Q2.G = 0.570;        

Q2.nu_x = 0.018;

% in, nominal
Q2.h = 0.191 / 25.4;   

% ksi
Q2.Xt = 430;           
Q2.Xc = 258;           
Q2.Yt = 8.75;          
Q2.Yc = 31.0;          
Q2.S = 10;             

%% Coupon

% Degrees (top to bottom)
angles1 = [
     0   90   90    0;
     0    0   90   90;
];
angles2 = [
     0    0    0    0;
     0   90   90    0;
     0    0   90   90;
    30  -30  -30   30;
    45   45  -45  -45;
    45  -45  -45   45;
     0   60   60    0;
     0   45  -45   90;
    90    0    0    0;
    90   90    0   90
];

% cm
dimensions = [
    25.5  2.70  0.077;
    30.6  2.67  0.077;
    30.5  2.67  0.076;
    25.8  2.76  0.077;
    25.6  2.70  0.075;
    25.8  2.80  0.075;
    25.5  2.75  0.076;
    25.4  2.66  0.077;
    25.4  2.70  0.078;
    25.5  2.74  0.077
];

h_p1 = size(angles1,2) * Q1.h * ones(size(angles1,1),1);
h_p2 = dimensions(:,3) / 2.54; % covnerting

%% Problem 1

deltaT = 75 - 400;

laminate1 = make_laminate(Q1, angles1, h_p1);
[N1,M1] = determine_N_M(laminate1, Q1, deltaT);
[ep1,k1] = midplane(laminate1, N1, M1);
[resid1] = residuals(laminate1, Q1, ep1, deltaT, k1);

print_p1 = true;
if print_p1
    fprintf('\n==================== Part (a) ====================\n');
    for i = 1:size(angles1,1)
        fprintf('\nSpecimen %d\n', i);
        disp('N (lbf/in):');
        disp(1e6 * N1(:,i));
        disp('M (lbf):');
        disp(1e6 * M1(:,i));
    end

    fprintf('\n==================== Part (b) ====================\n');
    for i = 1:size(angles1,1)
        fprintf('\nSpecimen %d\n', i);
        disp('Global midplane strain [epsX; epsY; gammaXY]:');
        disp(ep1(:,i));
        disp('Curvature [kX; kY; kXY] (1/in):');
        disp(k1(:,i));
    end

    fprintf('\n==================== Part (c) ====================\n');
    disp('Columns: top, bottom of each ply. Strains are dimensionless.');
    for i = 1:size(angles1,1)
        fprintf('\n==================== Specimen %d ====================\n', i);
        for j = 1:size(angles1,2)
            fprintf('\nPly %d (%g deg)\n', j, angles1(i,j));
            disp('Local residual stress [sigma1; sigma2; tau12] (ksi):');
            disp(resid1.sigma(:,:,j,i));
            disp('Global total strain [epsX; epsY; gammaXY]:');
            disp(resid1.eps_total(:,:,j,i));
            disp('Global elastic strain [epsX; epsY; gammaXY]:');
            disp(resid1.eps_elastic(:,:,j,i));
        end
    end
end

%% Problem 2
laminate2 = make_laminate(Q2, angles2, h_p2);
Lg_mm = dimensions(:,1) * 10; % Use supplied Part 2 lengths, cm -> mm.
alpha11 = squeeze(laminate2.alphas(1,1,:));
K2 = 1e6 * 4.44822 * (dimensions(:,2)/2.54) ./ (alpha11 .* Lg_mm); % N/mm

hw4_dir = fileparts(mfilename('fullpath'));

figure('Theme','light','Position',[100 100 1000 1300]);
tiledlayout(5,2);
for i = 1:10
    nexttile; hold on;
    file = sprintf('layup%d.dat',i);
    if i == 1, file = 'layup1p2.dat'; end
    data = readmatrix(fullfile(hw4_dir,'tensile_data',file), ...
        'FileType','text','NumHeaderLines',8);
    data = data(all(isfinite(data(:,1:6)),2),1:6); % Skip repeated headers.
    force = data(:,3) - data(1,3); % N
    extension = data(:,4) - data(1,4); % mm
    plot(extension,force);
    extension = [0 max(extension)];
    plot(extension,K2(i)*extension,'k--');
    title(sprintf('Coupon %d [%g/%g/%g/%g]',i,angles2(i,:)));
    xlabel('Axial displacement (mm)'); ylabel('Load (N)');
    grid on;
end
sgtitle('Q2: full experimental curves and linear elastic theory');
exportgraphics(gcf,fullfile(hw4_dir,'hw4_q2.png'),'Resolution',180);
% exportgraphics(gcf,fullfile(hw4_dir,'hw4_q2.pdf'),'ContentType','vector');
snapnow;


% Coupons with fibers aligned with the 0 degree direction align closest with the linear elasticity theory and give more linear response.
% Coupon 9 agrees especially well because it has 3 of 4 of its plies oriented at 0.
% But Coupon 1, with all 4 fibers in that direction, performs worse than expected,
% showing that the alignment alone does not account for the results, and this may be potentially due to a resin failure,
% and how one 90 degree ply of Coupon 9 might hold it transversely better. 

% Asymmetric one, such as Coupons 3 and 5, have coupling between stretching and bending,
% making their response more sensitive to the geometry of the test setup and the method with which they are secured.
% Coupon 6, despite having ±45° fibers, performs exceptionally well, and its extension/bending coupling is not as present as in asymmetric coupons like Coupon 5.


%% Functions

function [laminate] = make_laminate(material, angles, h)
    % h is total specimen thickness in inches.
    laminate.h = h;
    laminate.angles = angles;

    nu_y = material.Ey / material.Ex * material.nu_x;
    laminate.Q = cast([
        material.Ex/(1-material.nu_x*nu_y) material.nu_x*material.Ey/(1-material.nu_x*nu_y) 0;
        material.nu_x*material.Ey/(1-material.nu_x*nu_y) material.Ey/(1-material.nu_x*nu_y) 0;
        0 0 material.G
        ], "double");

    laminate.T = @(x) [
        cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
        sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
        -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];


    [laminate.As,laminate.Bs,laminate.Ds,laminate.alphas,laminate.betas,laminate.deltas] = laminate_matrices(laminate.Q, angles, laminate.T, h);
end

function [forces, moments] = determine_N_M(laminate, material, deltaT)
    % thermal strain 
    e_t = [material.alpha_x material.alpha_y 0]' * deltaT;
    [n, n_layers] = size(laminate.angles);
    forces = zeros(3,n);
    moments = zeros(3,n);

    for i = 1:n

        % Each layer
        z = linspace(-laminate.h(i)/2, laminate.h(i)/2, n_layers + 1);
        for k = 1:n_layers
            T = laminate.T(deg2rad(laminate.angles(i,k)));
            Qbar = T \ laminate.Q / T';
            e_t_glob = T' * e_t;
            forces(:,i) = forces(:,i) + Qbar * e_t_glob * (z(k+1) - z(k));
            moments(:,i) = moments(:,i) + Qbar * e_t_glob * (z(k+1)^2 - z(k)^2) / 2;
        end
    end

end

function [ep_midplane, k_midplane] = midplane(laminate, N, M)
    ep_midplane = zeros(size(N));
    k_midplane = zeros(size(M));
    for i = 1:size(N,2)
        ep_midplane(:,i) = laminate.alphas(:,:,i) * N(:,i) + laminate.betas(:,:,i) * M(:,i);
        k_midplane(:,i) = laminate.betas(:,:,i)' * N(:,i) + laminate.deltas(:,:,i) * M(:,i);
    end
end

function [resid] = residuals(laminate, material, ep_mid, deltaT, k_mid)
    e_t = [material.alpha_x material.alpha_y 0]' * deltaT;
    [n, n_layers] = size(laminate.angles);

    resid.N = zeros(3,n_layers,n);
    resid.M = zeros(3,n_layers,n);

    % 2 for top and bottom
    resid.sigma = zeros(3,2,n_layers,n);
    % Global strains, also 2
    resid.eps_total = zeros(3,2,n_layers,n);
    resid.eps_elastic = zeros(3,2,n_layers,n);

    for i = 1:n
        z = linspace(-laminate.h(i)/2, laminate.h(i)/2, n_layers + 1);
        for k = 1:n_layers
            T = laminate.T(deg2rad(laminate.angles(i,k)));
            Qbar = T \ laminate.Q / T';
            e_R = ep_mid(:,i) - T' * e_t;
            z0 = z(k);
            z1 = z(k+1);
            resid.eps_total(:,:,k,i) = ep_mid(:,i) + k_mid(:,i) * [z0 z1];
            resid.eps_elastic(:,:,k,i) = resid.eps_total(:,:,k,i) - T' * e_t;

            resid.N(:,k,i) = Qbar * (e_R * (z1-z0) + k_mid(:,i) * (z1^2-z0^2)/2);
            resid.M(:,k,i) = Qbar * (e_R * (z1^2-z0^2)/2 + k_mid(:,i) * (z1^3-z0^3)/3);
            resid.sigma(:,:,k,i) = 1e3 * T * Qbar * resid.eps_elastic(:,:,k,i);
        end
    end
end

