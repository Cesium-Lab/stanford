close all
clear all
clc

%% Part c

function [x_dot] = cart_fixed_ode(t, x, l, g)
    theta_dot = x(1);
    phi = x(2);

    theta_dot_dot = - g / l * sin(phi);


    x_dot = [theta_dot_dot; theta_dot];
end



%                               phi_dot, phi
cart_fixed_initial_conditions_1 = [  0;     0  ];
cart_fixed_initial_conditions_2 = [  0;     5*pi/180  ];
cart_fixed_initial_conditions_3 = [  0;     10*pi/180  ];
cart_fixed_initial_conditions_4 = [  0;     15*pi/180  ];
cart_fixed_initial_conditions_5 = [  0;     30*pi/180  ];
cart_fixed_initial_conditions_6 = [  0;     60*pi/180  ];

tspan = [0, 10];

m = 1; % kg
l = 2; % m
k = 5; % N/m
M = 2; % kg
g = 9.81; % m/s2

fprintf("omega: %.2d rad/s\n", sqrt(g/l))
fprintf("period: %.2d s\n", 2 * pi / sqrt(g/l))

[t1,y1] = ode45(@(t,y) cart_fixed_ode(t, y, l, g), ...
    tspan, cart_fixed_initial_conditions_1);
[t2,y2] = ode45(@(t,y) cart_fixed_ode(t, y, l, g), ...
    tspan, cart_fixed_initial_conditions_2);
[t3,y3] = ode45(@(t,y) cart_fixed_ode(t, y, l, g), ...
    tspan, cart_fixed_initial_conditions_3);
[t4,y4] = ode45(@(t,y) cart_fixed_ode(t, y, l, g), ...
    tspan, cart_fixed_initial_conditions_4);
[t5,y5] = ode45(@(t,y) cart_fixed_ode(t, y, l, g), ...
    tspan, cart_fixed_initial_conditions_5);
[t6,y6] = ode45(@(t,y) cart_fixed_ode(t, y, l, g), ...
    tspan, cart_fixed_initial_conditions_6);

figure(1)
hold on
plot(t2, y2(:,2))
plot(t3, y3(:,2))
plot(t4, y4(:,2))
plot(t5, y5(:,2))
plot(t6, y6(:,2))
hold off
title("Fixed Cart")
legend('5 deg', '10 deg', '15 deg', '30 deg', '60 deg')
xlabel("Time (s)")
ylabel("phi (rad)")

%% Part d


function dydt = cart_moving_ode(t, y, l, g, m, M, k)
    x_dot = y(1); x = y(2);
    phi_dot = y(3); phi = y(4);
    
    A = [cos(phi), l;   m + M, m*l*cos(phi)];

    b = [-g * sin(phi); m * phi_dot^2*l*sin(phi) - k*x];
     
    dot_dot_vec = A\b;  % solve for [x_ddot; phi_ddot]
    x_dot_dot = dot_dot_vec(1);
    phi_dot_dot = dot_dot_vec(2);

    dydt = [x_dot_dot; x_dot; phi_dot_dot; phi_dot];
end

%                                   x_dot, x,phi_dot, phi
cart_moving_initial_conditions_1 = [  0.5; 0; 0;     0  ];
cart_moving_initial_conditions_2 = [  0.5; 0; 0;     5*pi/180  ];
cart_moving_initial_conditions_3 = [  0.5; 0; 0;     10*pi/180  ];
cart_moving_initial_conditions_4 = [  0.5; 0; 0;     15*pi/180  ];
cart_moving_initial_conditions_5 = [  0.5; 0; 0;     30*pi/180  ];
cart_moving_initial_conditions_6 = [  0.5; 0; 0;     60*pi/180  ];

tspan = [0, 10];

m = 1; % kg
l = 2; % m
k = 5; % N/m
M = 2; % kg
g = 9.81; % m/s2

fprintf("omega: %.2d rad/s\n", sqrt(g/l))
fprintf("period: %.2d s\n", 2 * pi / sqrt(g/l))

[t1,y1] = ode45(@(t,y) cart_moving_ode(t, y, l, g, m, M, k), ...
    tspan, cart_moving_initial_conditions_1);
[t2,y2] = ode45(@(t,y) cart_moving_ode(t, y, l, g, m, M, k), ...
    tspan, cart_moving_initial_conditions_2);
[t3,y3] = ode45(@(t,y) cart_moving_ode(t, y, l, g, m, M, k), ...
    tspan, cart_moving_initial_conditions_3);
[t4,y4] = ode45(@(t,y) cart_moving_ode(t, y, l, g, m, M, k), ...
    tspan, cart_moving_initial_conditions_4);
[t5,y5] = ode45(@(t,y) cart_moving_ode(t, y, l, g, m, M, k), ...
    tspan, cart_moving_initial_conditions_5);
[t6,y6] = ode45(@(t,y) cart_moving_ode(t, y, l, g, m, M, k), ...
    tspan, cart_moving_initial_conditions_6);

figure(2)
hold on
plot(t2, y2(:,4))
plot(t3, y3(:,4))
plot(t4, y4(:,4))
plot(t5, y5(:,4))
plot(t6, y6(:,4))
hold off
title("Moving Cart")
legend('5 deg', '10 deg', '15 deg', '30 deg', '60 deg')
xlabel("Time (s)")
ylabel("phi (rad)")