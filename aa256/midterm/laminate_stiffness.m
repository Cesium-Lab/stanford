function [A, B, D, alpha, beta, delta, Q_bar, Ts, z] = laminate_stiffness(Q, angles, h)

n_layers = length(angles);
z = [-sum(h)/2, -sum(h)/2 + cumsum(h(:)')];
A = zeros(3); B = zeros(3); D = zeros(3);
Q_bar = zeros(3,3,n_layers);
Ts = zeros(3,3,n_layers);


for k = 1:n_layers
    T = plane_transformation(deg2rad(angles(k)));
    Ts(:,:,k) = T;
    Q_bar(:,:,k) = T \ Q(:,:,k) / T';
    z0 = z(k); z1 = z(k+1);
    A = A + Q_bar(:,:,k) * (z1-z0);
    B = B + Q_bar(:,:,k) * (z1^2-z0^2) / 2;
    D = D + Q_bar(:,:,k) * (z1^3-z0^3) / 3;
end

compliance = [A B; B' D] \ eye(6);

alpha = compliance(1:3,1:3);
beta = compliance(1:3,4:6);
delta = compliance(4:6,4:6);
end
