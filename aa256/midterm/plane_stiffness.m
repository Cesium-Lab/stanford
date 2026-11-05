function Q = plane_stiffness(Ex, Ey, G, nu_x, nu_y)
% Plane stress; local strain order [eps_x; eps_y; gamma_xy].
% Reciprocity: nu_y = Ey / Ex * nu_x.
Q = [Ex nu_x*Ey 0;
     nu_y*Ex Ey 0;
     0 0 G*(1-nu_x*nu_y)] / (1-nu_x*nu_y);
end
