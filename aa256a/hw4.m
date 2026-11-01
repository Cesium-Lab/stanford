clc
clear
close all
format short g

%% Materials

% Q1: T800/3900-2
Q1.Ex = 23.2;          % Msi
Q1.Ey = 1.30;          % Msi
Q1.G = 0.90;           % Msi
Q1.nu_x = 0.28;
Q1.alpha1 = -6.8e-6;   % 1/deg F
Q1.alpha2 = 32e-6;     % 1/deg F
Q1.h = 0.007;          % in

Q1.Xt = 412;           % ksi
Q1.Xc = 225;           % ksi
Q1.Yt = 10;            % ksi
Q1.Yc = 24.3;          % ksi
Q1.S = 10;             % ksi

% Q2: T800SC/3900-2B
Q2.Ex = 21.5;          % Msi
Q2.Ey = 1.20;          % Msi
Q2.G = 0.570;          % Msi
Q2.nu_x = 0.018;
Q2.h = 0.191 / 25.4;   % in, nominal

Q2.Xt = 430;           % ksi
Q2.Xc = 258;           % ksi
Q2.Yt = 8.75;          % ksi
Q2.Yc = 31.0;          % ksi
Q2.S = 10;             % ksi

%% Coupon

% Degrees (top to bottom)
angles = [
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
[N, N_layers] = size(angles);

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

% Select the material used for this calculation.
material = Q1;
laminate1 = problem1(material, angles, dimensions);


function [out] = problem1(material, angles, dimensions)
    % cm -> in
    h = dimensions(:,3) * 2.54;

    nu_y = material.Ey / material.Ex * material.nu_x;
    out.Q = cast([
        material.Ex/(1-material.nu_x*nu_y) material.nu_x*material.Ey/(1-material.nu_x*nu_y) 0;
        material.nu_x*material.Ey/(1-material.nu_x*nu_y) material.Ey/(1-material.nu_x*nu_y) 0;
        0 0 material.G
        ], "double");

    out.T = @(x) [
        cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
        sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
        -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];


    [out.As,out.Bs,out.Ds,out.alphas,out.betas,out.deltas] = laminate_matrices(out.Q, angles, out.T, h);
end

function [forces, moments] = determine_N_M(out, material, deltaT)
    % thermal strain
    
end