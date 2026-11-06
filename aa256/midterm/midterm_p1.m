clear all
clc
close all

%% Properties
Ex = 23.2; Ey = 1.3; G = 0.90; % Msi
nu_x = 0.28;
nu_y = Ey / Ex * nu_x;

angles = [30 -45 60 0];
n_layers = length(angles);
h = 0.007 * ones(1,n_layers); % Individual ply thicknesses, in.

alphas = repmat([-6.8e-6; 32e-6; 0],1,n_layers);
betas = zeros(3,n_layers);

deltaT = (75-400) * ones(1,n_layers); 
deltaC = zeros(1,n_layers);

% %% Calculating T
% theta = deg2rad(20);
% [T, T_eps] = plane_transformation(theta)
% for k = 1:n_layers
%     T = plane_transformation(deg2rad(angles(k)));
% end

%% Calculating Q_bar

Q = plane_stiffness(Ex,Ey,G,nu_x,nu_y)
% Q_bar_theta = T \ Q / T'

%% 4-5. Layer stiffnesses, A/B/D and full inverse blocks
% For mixed materials, replace each Q_layers(:,:,k) with that ply's Q.
Q_layers = repmat(Q,1,1,n_layers);
[A,B,D,alpha,beta,delta,Q_bar,Ts,z] = ...
    laminate_stiffness(Q_layers,angles,h);
A, B, D, alpha, beta, delta
Ts
Q_bar

%% 5-8. Thermal + moisture response and residual stresses
[ep_mid,k_mid,N_nm,M_nm,ep_free,ep_constrained,ep_residual,sigma_global,sigma_local] = ...
    nonmechanical_response(Q_bar,Ts,z,alpha,beta,delta,alphas,betas,deltaT,deltaC);

N_nm * 1e6 % lb/in
M_nm * 1e6 % lb/in
ep_mid
k_mid
