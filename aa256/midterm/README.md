Run `midterm_example.m` with this folder as MATLAB's current folder. Edit its input section; all eight steps leave their intermediate results in the workspace. Functions contain formulas only, with no input validation.

- `plane_transformation(theta)`: 2D stress and engineering-strain transformations; radians, global to local.
- `rotation_matrices(theta_x,theta_y,theta_z)`: fundamental rotations and 3D stress/engineering-strain transformations; radians.
- `plane_stiffness(Ex,Ey,G,nu_x,nu_y)`: local plane-stress Q. Use nu_y = Ey/Ex*nu_x.
- `laminate_stiffness(Q_layers,angles,h)`: one laminate, ply angles in degrees, individual thickness vector, and one Q per ply. Returns A/B/D, alpha/beta/delta, all Q_bar and T matrices, and interface z coordinates.
- `nonmechanical_response(...)`: equivalent thermal/moisture loads, compatible strains, isolated-ply free strains, residual elastic strains, and global/local residual stresses.

Conventions follow HW3/HW4: stack top to bottom, z positive downward, eps(z) = eps_mid + z*k_mid. All plane strains use engineering shear. Face results have dimensions 3 x 2 x n_layers, with top/bottom in columns. Expansion coefficients have dimensions 3 x n_layers. Temperature and concentration changes have one entry per ply, constant within each ply. Use concentration units consistent with the moisture coefficients.

Laminar constraint means compatibility between bonded plies. There are no external clamps or applied loads. Alpha/beta/delta are the full ABD inverse blocks; they are not thermal expansion coefficients. Residual elastic strain is compatible laminate strain minus the isolated-ply thermal-plus-moisture free strain. Stress uses Q_bar in global axes or T*sigma_global in local axes.

The example uses Msi and inches; stress outputs are converted to ksi. Moisture coefficients and concentration changes default to zero because the supplied HW4 example is thermal only. Fill these with problem data to include moisture.

Checks: independent Python evaluation matches HW2 Q_bar at 20 degrees and HW4 midplane strain/curvature for both [0/90/90/0] and [0/0/90/90]. Integrated residual force and moment vanish. MATLAB/Octave were unavailable, so the MATLAB files have not been executed here.

Corrections relative to existing homework code: HW1 Tx row 4 should start [0,-cs,+cs,...]; the rotation function uses these signs. The existing laminate_matrices indexes h(i) although HW3 supplies a scalar for several specimens; the new function works on one laminate with explicit individual ply thicknesses. Original homework files are unchanged.
