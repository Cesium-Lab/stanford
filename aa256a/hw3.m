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



%% Problem 2

angles2 = angles + 15;
[As2,Bs2,Ds2,alphas2,betas2,deltas2] = matrices(Q, angles2, T, h);

alpha11 = squeeze(alphas2(1,1,:));
E11 = 1./alpha11/h/N_layers % Msi


%% Func
function [As,Bs,Ds,alphas,betas,deltas] = matrices(Q, angles, T_func, h)

    [N, N_layers] = size(angles);
    
    % Iterates through all specimens
    for i = 1:N
        Qbar = zeros(3, 3);
        for layer = 1:N_layers
            angle = deg2rad(angles(i, layer));
            transformation = T_func(angle);
            Qbar = Qbar + transformation \ Q / transformation';
        end
    
        z = h*i;
        zp = h*(i-1);
    
        As(:,:,i) = h * Qbar;
        Bs(:,:,i) = (z^2 - zp^2) * Qbar / 2;
        Ds(:,:,i) = (z^3 - zp^3) * Qbar / 3;
    
        big = [squeeze(As(:,:,i)) squeeze(Bs(:,:,i)); squeeze(Bs(:,:,i)) squeeze(Ds(:,:,i))]';
        alphas(:,:,i) = big(1:3,1:3);
        betas(:,:,i) = big(1:3,4:6);
        deltas(:,:,i) = big(4:6,4:6);
    
    end
end