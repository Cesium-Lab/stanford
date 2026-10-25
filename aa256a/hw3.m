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

[As,Bs,Ds,alphas,betas,deltas] = matrices(Q, angles, T, h);

As
Bs
Ds
alphas
betas
deltas


%% Problem 2

angles2 = angles + 15;
[As2,Bs2,Ds2,alphas2,betas2,deltas2] = matrices(Q, angles2, T, h);

Bs2
Ds2
alphas2
betas2
deltas2

alpha11 = squeeze(alphas2(1,1,:));
E11 = 1./alpha11/h/N_layers % Msi


%% Func
function [As,Bs,Ds,alphas,betas,deltas] = matrices(Q, angles, T_func, h)

    [N, N_layers] = size(angles);

    z = ((0:N_layers) - N_layers/2)*h;

    As = zeros(3,3,N);
    Bs = zeros(3,3,N);
    Ds = zeros(3,3,N);

    alphas = zeros(3,3,N);
    betas  = zeros(3,3,N);
    deltas = zeros(3,3,N);
    
    % Iterates through all specimens
    for i = 1:N

        A = zeros(3);
        B = zeros(3);
        D = zeros(3);

        for k = 1:N_layers
            angle = deg2rad(angles(i, k));
            transformation = T_func(angle);
            Qbar = transformation \ Q / transformation';

            z0 = z(k);
            z1 = z(k+1);

            A = A + (z1 - z0) * Qbar;
            B = B + (z1^2 - z0^2) * Qbar / 2;
            D = D + (z1^3 - z0^3) * Qbar / 3;

        end
    

    
        ABD = [A B; B' D];
        compliance = ABD \ eye(6);

        As(:,:,i) = A;
        Bs(:,:,i) = B;
        Ds(:,:,i) = D;
        
       
        alphas(:,:,i) = compliance(1:3,1:3);
        betas(:,:,i) = compliance(1:3,4:6);
        deltas(:,:,i) = compliance(4:6,4:6);
    
    end
end