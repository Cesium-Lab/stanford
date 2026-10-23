clc
clear all
close all

unit_vector = sprintf('%.4f ', [1 -2 4] / norm([1 -2 4]));
fprintf("4.1: Unit vector = [ %s]\n\n", unit_vector)

v1 = [1 -2 3];
v2 = [3 1 4];

angle_between = acos( dot(v1, v2) / norm(v1) / norm(v2));
fprintf("4.2: Angle between = %.2f rad\n\n", angle_between);

x = linspace(-2, 2, 100);
y = linspace(-1, 1, 100);
[X,Y] = meshgrid(x,y);

Z = (X.^3 - 3*X) .* (2*Y.^3 - Y);

U = (3*X.^2 - 3) .* (2*Y.^3 - Y);
V = (X.^3 - 3*X) .* (6*Y.^2 - 1);
figure(1)
hold on
contour(X, Y, Z, 40)
quiver(X, Y, U, V, 2)
hold off
saveas(gcf, "contours.png")


%% ODE

function [x_dot] = odefun(t, x, a, b, c)
    x1 = x(1);
    x2 = x(2);
    y1 = x(3);
    y2 = x(4);

    dx1 = y1;
    dx2 = y2;
    dy1 = -a * x1 + b * (x2 - x1);
    dy2 = -c * (x2 - x1);

    x_dot = [dx1; dx2; dy1; dy2];
end

initial_conditions = [1; 1; 0; 0];

tspan = [0, 100];

[t1,y1] = ode45(@(t,y) odefun(t, y, 4, 1, 7.5), tspan, initial_conditions);
[t2,y2] = ode45(@(t,y) odefun(t, y, 1, 1, 1.5), tspan, initial_conditions);

figure(2)

subplot(3,3,1:3)
plot(t1, y1(:,1))
title("Scenario 'a' x1")
legend('x1')
xlabel("Time (s)")
ylabel("Amplitude")

subplot(3,3,4:6)
plot(t1, y1(:,2))
title("Scenario 'a' x2")
legend('x2')
xlabel("Time (s)")
ylabel("Amplitude")

subplot(3,3,7:9)
plot(t1, y1(:,1) + y1(:,2))
title("Scenario 'a' x1 + x2")
legend('x1 + x2')
xlabel("Time (s)")
ylabel("Amplitude")

saveas(gcf, "scenario_a.png")

figure(3)

subplot(3,3,1:3)
plot(t2, y2(:,1))
title("Scenario 'b' x1")
legend('x1')
xlabel("Time (s)")
ylabel("Amplitude")

subplot(3,3,4:6)
plot(t2, y2(:,2))
title("Scenario 'b' x2")
legend('x2')
xlabel("Time (s)")
ylabel("Amplitude")

subplot(3,3,7:9)
plot(t2, y2(:,1) + y2(:,2))
title("Scenario 'b' x1 + x2")
legend('x1 + x2')
xlabel("Time (s)")
ylabel("Amplitude")

saveas(gcf, "scenario_b.png")