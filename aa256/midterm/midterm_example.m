clc
clear
close all
format short g

%% Inputs: HW4 thermal example. Edit these for a different problem.
Ex = 23.2; Ey = 1.3; G = 0.90; % Msi
nu_x = 0.28;
nu_y = Ey / Ex * nu_x;
angles = [0 0 90 90]; % Degrees, top to bottom; try [0 90 90 0].
n_layers = length(angles);
h = 0.007 * ones(1,n_layers); % Individual ply thicknesses, in.
a = repmat([-6.8e-6; 32e-6; 0],1,n_layers); % Thermal, 1/deg F.
b = zeros(3,n_layers); % Moisture expansion per concentration unit.
deltaT = (75-400) * ones(1,n_layers); % Final minus stress-free temperature.
deltaC = zeros(1,n_layers); % Final minus stress-free moisture concentration.

%% 1. Stress and engineering-strain transformations
theta = deg2rad(20);
[T, T_eps] = plane_transformation(theta)
[Rx,Ry,Rz,Tx,Ty,Tz,Tx_eps,Ty_eps,Tz_eps] = ...
    rotation_matrices(deg2rad(90),deg2rad(30),deg2rad(45));
rotation = Rz*Ry*Rx
T_3D = Tz*Ty*Tx
T_eps_3D = Tz_eps*Ty_eps*Tx_eps

%% 2. Local plane-stress stiffness
Q = plane_stiffness(Ex,Ey,G,nu_x,nu_y)

%% 3. Global stiffness at theta (20 degrees here)
Q_bar_theta = T \ Q / T'

%% 4-5. Layer stiffnesses, A/B/D and full inverse blocks
% For mixed materials, replace each Q_layers(:,:,k) with that ply's Q.
Q_layers = repmat(Q,1,1,n_layers);
[A,B,D,alpha,beta,delta,Q_bar,Ts,z] = ...
    laminate_stiffness(Q_layers,angles,h);
A, B, D, alpha, beta, delta

%% 5-8. Thermal + moisture response and residual stresses
[ep_mid,k_mid,N_nm,M_nm,ep_free,ep_constrained,ep_residual,sigma_global,sigma_local] = ...
    nonmechanical_response(Q_bar,Ts,z,alpha,beta,delta,a,b,deltaT,deltaC);
% Equivalent loads, not actual applied force or moment.
N_nm_lbf_per_in = 1e6*N_nm
M_nm_lbf = 1e6*M_nm
ep_mid
k_mid % 1/in, engineering twist convention.
ep_free % Global free strains: one column per isolated ply.
for k = 1:n_layers
    fprintf('\nPly %d (%g deg): columns = top, bottom\n',k,angles(k));
    disp('Compatible global strain:'); disp(ep_constrained(:,:,k));
    disp('Residual elastic global strain:'); disp(ep_residual(:,:,k));
    disp('Residual global stress (ksi):'); disp(1e3*sigma_global(:,:,k));
    disp('Residual local stress (ksi):'); disp(1e3*sigma_local(:,:,k));
end
