function [ep_mid, k_mid, N_nm, M_nm, ep_free, ep_constrained, ep_residual, sigma_global, sigma_local] = nonmechanical_response(Q_bar, Ts, z, alpha, beta, delta, a, b, deltaT, deltaC)

n_layers = size(Q_bar,3);
ep_free = zeros(3,n_layers);
N_nm = zeros(3,1); M_nm = zeros(3,1);
for k = 1:n_layers
    ep_free(:,k) = Ts(:,:,k)' * (a(:,k)*deltaT(k) + b(:,k)*deltaC(k));
    N_nm = N_nm + Q_bar(:,:,k)*ep_free(:,k)*(z(k+1)-z(k));
    M_nm = M_nm + Q_bar(:,:,k)*ep_free(:,k)*(z(k+1)^2-z(k)^2)/2;
end

ep_mid = alpha*N_nm + beta*M_nm;
k_mid = beta'*N_nm + delta*M_nm;

ep_constrained = zeros(3,2,n_layers);
ep_residual = zeros(3,2,n_layers);
sigma_global = zeros(3,2,n_layers);
sigma_local = zeros(3,2,n_layers);

for k = 1:n_layers
    ep_constrained(:,:,k) = ep_mid + k_mid*[z(k) z(k+1)];
    ep_residual(:,:,k) = ep_constrained(:,:,k) - ep_free(:,k);
    sigma_global(:,:,k) = Q_bar(:,:,k)*ep_residual(:,:,k);
    sigma_local(:,:,k) = Ts(:,:,k)*sigma_global(:,:,k);
end
end
