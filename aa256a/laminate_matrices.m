%% Func
function [As,Bs,Ds,alphas,betas,deltas] = laminate_matrices(Q, angles, T_func, h)

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