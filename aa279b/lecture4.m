mu = 398600;
R = 6378;

n = sqrt(mu/(R + 300)^3); % 1/s

tf = 20*60;


[Phi_rr, Phi_rv, Phi_vr, Phi_vv] = Phi(tf, n);

r0 = [30 150]'

v0 = -Phi_rv \ Phi_rr * r0
vf = Phi_vr*r0 + Phi_vv*v0

t = linspace(0, 20*60, 1000);

r = zeros(2, 1000);
v = zeros(2, 1000);
for i=1:1000

    [Phi_rr, Phi_rv, Phi_vr, Phi_vv] = Phi(t(i), n);
    r(:,i) = Phi_rr * r0 + Phi_rv * v0;
    v(:,i) = Phi_vr * r0 + Phi_vv * v0;
    
end

figure()
plot(-r(2,:), r(1,:))
grid("on")
%%

function [Phi_rr, Phi_rv, Phi_vr, Phi_vv] = Phi(t,n)

    c = cos(n*t);
    s = sin(n*t);
    
    Phi_rr = [4-3*c 0; 6*(s - n*t) 1];
    Phi_rv = 1/n * [s 2*(1 - c); 2*(c - 1) (4*s - 3*n*t)];
    
    Phi_vr = [3*n*s 0; 6*n*(c-1) 0];
    Phi_vv = [c 2*s; -2*s 4*c-3];

end