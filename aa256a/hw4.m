clc
clear
close all
format short g

%% Conversions
CM_TO_IN = 1 / 2.54;
mm_to_in = 1 / 25.4;
LBF_TO_N = 4.44822;
PSI_TO_MPA = 0.00689476;


%% Materials

% Q1: T800/3900-2
% Msi
Ex = 23.2;          
Ey = 1.30;          
G = 0.90;           
nu_x = 0.28;
nu_y = Ey / Ex * nu_x;
alpha1 = -6.8e-6;   % 1/deg F
alpha2 = 32e-6;     % 1/deg F
% h = 0.007;          % in

% ksi
% Xt = 412;           
% Xc = 225;           
% Yt = 10;            
% Yc = 24.3;          
S = 10.0;           

% T800SC/3900-2B
% Msi
Ex2 = 21.5;         
Ey2 = 1.20;         
G2 = 0.570;         
nu_x2 = 0.018;
nu_y2 = Ey2 / Ex2 * nu_x2;
% h2_nominal = 0.191; % mm

% ksi
% Xt2 = 430;          
% Xc2 = 258;          
% Yt2 = 8.75;         
% Yc2 = 31.0;         
S2 = 10.0;          

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

lengths = dimensions(:,1);      % cm
widths = dimensions(:,2);       % cm
thicknesses = dimensions(:,3);  % cm



% Dimensions in inches
lengths_in = lengths * CM_TO_IN;
widths_in = widths * CM_TO_IN;
thicknesses_in = thicknesses * CM_TO_IN;

% Measured ply thickness for each
h = thicknesses_in;
h2 = thicknesses_in / 4;

Q = cast([
    Ex/(1-nu_x*nu_y)      nu_x*Ey/(1-nu_x*nu_y) 0;
    nu_y*Ex/(1-nu_x*nu_y) Ey/(1-nu_x*nu_y) 0;
    0 0 G
    ], "double");

T = @(x) [
    cos(x)*cos(x)   sin(x)*sin(x)  2*cos(x)*sin(x);
    sin(x)*sin(x)   cos(x)*cos(x) -2*cos(x)*sin(x);
    -sin(x)*cos(x) sin(x)*cos(x)   cos(x)*cos(x)-sin(x)*sin(x)];


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

% 
% 
% %% Problem 2
% angles2 = angles - 15;
% [As2,Bs2,Ds2,alphas2,betas2,deltas2] = laminate_matrices(Q, angles2, T, h);
% names = {'A', 'B', 'D', 'alpha', 'beta', 'delta'};
% matrices = {As2, Bs2, Ds2, alphas2, betas2, deltas2};
% 
% fprintf('\n==================== Problem 2 ====================\n');
% fprintf('\n===== Sufficiently long specimen =====\n\n');
% 
% alpha11 = squeeze(alphas2(1,1,:));
% E11 = 1 ./ (alpha11 * h * N_layers);
% 
% fprintf('\nEffective Tensile Modulus E11:\n');
% 
% for i = 1:N
%     fprintf('Specimen %d: %.4f Msi\n', i, E11(i));
% end