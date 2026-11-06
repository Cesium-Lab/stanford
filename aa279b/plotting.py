import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline

from constants import R_EARTH, RAD_TO_DEG

import numpy as np
import plotly.graph_objects as go
from plotly.colors import qualitative
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

from constants import AU_TO_KM
from orbital import OrbitalFlyby

def _plotly_camera(elev, azim, projection, camera_distance):
    """Camera looking toward the origin, with angles measured in degrees."""
    if projection not in ("ortho", "persp"):
        raise ValueError("projection must be 'ortho' or 'persp'")
    if not np.all(np.isfinite([elev, azim, camera_distance])) or camera_distance <= 0:
        raise ValueError("Camera angles must be finite and camera_distance positive")
    el, az = np.deg2rad([elev, azim])
    return {
        "eye": {
            "x": camera_distance * np.cos(el) * np.cos(az),
            "y": camera_distance * np.cos(el) * np.sin(az),
            "z": camera_distance * np.sin(el),
        },
        "up": {"x": -np.sin(el) * np.cos(az),
               "y": -np.sin(el) * np.sin(az), "z": np.cos(el)},
        "projection": {"type": "orthographic" if projection == "ortho" else "perspective"},
    }

def _matplotlib_3d(
    plotly_fig, show=True,
    elev=np.rad2deg(np.arctan(1 / np.sqrt(2))), azim=45,
    projection="ortho",
):
    """Render the shared 3D geometry as a static Matplotlib figure."""
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection="3d")
    points = []
    data = plotly_fig.data
    for i, trace in enumerate(data):
        if trace.type == "cone":
            continue  # The preceding shaft supplies the complete arrow.
        xyz = [np.asarray(getattr(trace, k), dtype=float) for k in "xyz"]
        points.append(np.column_stack([a.ravel() for a in xyz]))
        if trace.type == "surface":
            ax.plot_surface(*xyz, color=trace.colorscale[0][1],
                            alpha=trace.opacity or 1, linewidth=0)
            continue
        label = trace.name if trace.showlegend is not False else "_nolegend_"
        if "lines" in trace.mode:
            color = trace.line.color
            if i + 1 < len(data) and data[i + 1].type == "cone":
                origin = np.array([a[0] for a in xyz])
                delta = np.array([a[-1] - a[0] for a in xyz])
                ax.quiver(*origin, *delta, color=color, label=label,
                          linewidth=2, arrow_length_ratio=0.10)
            else:
                ax.plot(*xyz, color=color, label=label)
        if "markers" in trace.mode:
            if trace.name == "Launch site":
                # Line3D markers respect zorder instead of being depth-sorted
                # as one collection against the entire Earth surface.
                ax.plot(*xyz, linestyle="none", marker="o", markersize=7,
                        color=trace.marker.color, markeredgecolor="white",
                        label=label, zorder=100)
            else:
                ax.scatter(*xyz, color=trace.marker.color, s=25, label=label)
        if "text" in trace.mode and trace.text is not None:
            for x, y, z, text in zip(*xyz, trace.text):
                ax.text(x, y, z, text, zorder=101)
    ax.set(xlabel=plotly_fig.layout.scene.xaxis.title.text,
           ylabel=plotly_fig.layout.scene.yaxis.title.text,
           zlabel=plotly_fig.layout.scene.zaxis.title.text,
           title=plotly_fig.layout.title.text)
    if points:
        all_points = np.concatenate(points)
        lo, hi = all_points.min(axis=0), all_points.max(axis=0)
        center = (lo + hi) / 2
        half = max(float(np.max(hi - lo)) / 2, 1) * 1.05
        ax.set_xlim(center[0] - half, center[0] + half)
        ax.set_ylim(center[1] - half, center[1] + half)
        ax.set_zlim(center[2] - half, center[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.set_proj_type(projection)
    ax.view_init(elev=elev, azim=azim)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)
    fig.tight_layout()
    if show:
        plt.show()
    return fig


def plot_3d(
    traces=None,
    t_arrs=None,
    labels=None,
    title="3D Trajectories",
    bodies=None,
    t_max=None,
    show_start=False,
    show_end=True,
    interpolate=False,
    n_interp=1000,
    units="km",
    height=800,
    show=True,
    vectors=None,
    trace_colors=None,
    elev=None,
    azim=None,
    projection="ortho",
    camera_distance=None,
):
    """Plot 3D trajectories, spherical bodies, and vector arrows.

    Parameters
    ----------
    traces : np.ndarray (N, 3) or list of np.ndarray, optional
        One or more 3D position trajectories.
    t_arrs : np.ndarray (N,) or list of np.ndarray, optional
        Time arrays, either shared or one per trajectory.
    labels : str or list of str, optional
        Trajectory labels.
    title : str
        Figure title.
    bodies : dict or list of dict, optional
        Spherical bodies with keys:
        'name', 'radius', 'center', 'color', 'opacity'.
    t_max : float, optional
        Maximum time to display.
    show_start, show_end : bool
        Show markers at trajectory endpoints.
    interpolate : bool
        Apply cubic spline interpolation to trajectories.
    n_interp : int
        Number of points per interpolated trajectory.
    units : str
        Position units for axis labels.
    height : int
        Figure height in pixels.
    vectors : dict or list of dict, optional
        Each arrow requires a nonzero "direction" (3,). Optional keys are
        "origin" (default zero), "length" (default direction magnitude, in
        plot units), "name", "color", and "width". Direction is normalized
        before applying length, allowing velocity vectors to be scaled for display.
    trace_colors : str or list of str, optional
        One color for all trajectories, or one color per trajectory.
    show : bool
        Display the figure immediately.
    elev, azim : float
        Camera elevation and azimuth in degrees; azimuth is measured from +x
        toward +y. Omitted angles use Plotly's default eye direction.
    projection : str
        "ortho" or "persp".
    camera_distance : float, optional
        Positive camera distance in Plotly scene units. By default choose a
        distance that frames the data. Larger values zoom out. Orthographic
        zoom scales the axis bounds because eye distance alone does not zoom.

    Returns
    -------
    fig : go.Figure
        Figure, whether or not it is displayed.
    """

    fig = go.Figure()

    # --------------------------------------------------
    # 1. Normalize trajectory inputs
    # --------------------------------------------------
    if traces is None:
        traces = []
    elif isinstance(traces, np.ndarray):
        if traces.ndim == 2:
            traces = [traces]
        elif traces.ndim == 3:
            traces = list(traces)
        else:
            raise ValueError("traces must have shape (N,3) or (K,N,3).")
    else:
        traces = list(traces)

    traces = [np.asarray(r, dtype=float) for r in traces]
    num_traces = len(traces)
    if isinstance(trace_colors, str):
        trace_colors = [trace_colors] * num_traces
    elif trace_colors is not None and len(trace_colors) != num_traces:
        raise ValueError("Number of trace colors must match trajectories.")


    # Labels
    if labels is None:
        labels = [f"Trajectory {i+1}" for i in range(num_traces)]
    elif isinstance(labels, str):
        labels = (
            [labels] if num_traces == 1
            else [f"{labels} {i+1}" for i in range(num_traces)]
        )

    if len(labels) != num_traces:
        raise ValueError("Number of labels must match trajectories.")

    # Time arrays: none, shared, or separate
    if t_arrs is None:
        times = [None] * num_traces
    elif len(t_arrs) > 0 and not np.isscalar(t_arrs[0]):
        times = [np.asarray(t) for t in t_arrs]
    else:
        times = [np.asarray(t_arrs)] * num_traces

    if len(times) != num_traces:
        raise ValueError("Number of time arrays must match trajectories.")

    if t_max is not None and t_arrs is None:
        raise ValueError("t_max requires time arrays.")

    # --------------------------------------------------
    # 2. Plot spherical bodies
    # --------------------------------------------------
    if bodies is not None:
        if isinstance(bodies, dict):
            bodies = [bodies]

        u = np.linspace(0, 2*np.pi, 60)
        v = np.linspace(0, np.pi, 30)

        sphere_x = np.outer(np.cos(u), np.sin(v))
        sphere_y = np.outer(np.sin(u), np.sin(v))
        sphere_z = np.outer(np.ones_like(u), np.cos(v))

        for body in bodies:
            radius = float(body["radius"])
            center = np.asarray(body.get("center", [0, 0, 0]))
            color = body.get("color", "royalblue")
            opacity = body.get("opacity", 0.7)

            if radius <= 0 or center.shape != (3,):
                raise ValueError("Body requires radius > 0 and center (3,).")

            fig.add_trace(go.Surface(
                x=radius*sphere_x + center[0],
                y=radius*sphere_y + center[1],
                z=radius*sphere_z + center[2],
                name=body.get("name", "Body"),
                colorscale=[[0, color], [1, color]],
                showscale=False,
                opacity=opacity,
                showlegend=False,
                hoverinfo="skip"
            ))

    # --------------------------------------------------
    # 3. Plot trajectories
    # --------------------------------------------------
    colors = qualitative.Plotly

    for idx, (t, r, label) in enumerate(zip(times, traces, labels)):

        if r.ndim != 2 or r.shape[1] != 3:
            raise ValueError(f"{label}: expected (N,3), got {r.shape}")

        if len(r) == 0 or not np.all(np.isfinite(r)):
            raise ValueError(f"{label}: invalid trajectory data.")

        if t is None:
            t = np.arange(len(r))
        else:
            t = np.asarray(t, dtype=float)

        if len(t) != len(r):
            raise ValueError(f"{label}: time and position lengths differ.")

        if not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
            raise ValueError(f"{label}: times must be finite and increasing.")

        # Clip time
        if t_max is not None:
            mask = t <= t_max
            t, r = t[mask], r[mask]

        if len(r) == 0:
            continue

        # Optional cubic spline interpolation
        if interpolate and len(r) >= 3:
            t_fine = np.linspace(t[0], t[-1], n_interp)
            r_plot = CubicSpline(t, r, axis=0)(t_fine)
        else:
            r_plot = r

        color = trace_colors[idx] if trace_colors is not None else colors[idx % len(colors)]

        # Trajectory
        fig.add_trace(go.Scatter3d(
            x=r_plot[:, 0],
            y=r_plot[:, 1],
            z=r_plot[:, 2],
            mode="lines",
            name=label,
            legendgroup=label,
            line={"color": color, "width": 5}
        ))

        # Start marker
        if show_start:
            fig.add_trace(go.Scatter3d(
                x=[r_plot[0, 0]],
                y=[r_plot[0, 1]],
                z=[r_plot[0, 2]],
                mode="markers",
                name=f"{label} Start",
                legendgroup=label,
                showlegend=False,
                marker={
                    "size": 6,
                    "color": color,
                    "symbol": "diamond"
                }
            ))

        # End marker
        if show_end:
            fig.add_trace(go.Scatter3d(
                x=[r_plot[-1, 0]],
                y=[r_plot[-1, 1]],
                z=[r_plot[-1, 2]],
                mode="markers",
                name=f"{label} End",
                legendgroup=label,
                showlegend=False,
                marker={"size": 6, "color": color}
            ))

    # Vector shafts and arrowheads share a legend entry.
    if vectors is not None:
        if isinstance(vectors, dict):
            vectors = [vectors]
        for idx, vector in enumerate(vectors):
            origin = np.asarray(vector.get("origin", [0, 0, 0]), dtype=float)
            direction = np.asarray(vector["direction"], dtype=float)
            if (origin.shape != (3,) or direction.shape != (3,)
                    or not np.all(np.isfinite(origin))
                    or not np.all(np.isfinite(direction))):
                raise ValueError("Vector origin and direction must be finite (3,) arrays.")
            magnitude = np.linalg.norm(direction)
            length = float(vector.get("length", magnitude))
            if magnitude == 0 or not np.isfinite(length) or length <= 0:
                raise ValueError("Vector direction must be nonzero and length positive and finite.")
            direction = direction / magnitude
            endpoint = origin + length * direction
            color = vector.get("color", colors[idx % len(colors)])
            name = vector.get("name", f"Vector {idx + 1}")
            group = f"vector-{idx}"
            fig.add_trace(go.Scatter3d(
                x=[origin[0], endpoint[0]], y=[origin[1], endpoint[1]],
                z=[origin[2], endpoint[2]], mode="lines", name=name,
                legendgroup=group,
                line={"color": color, "width": vector.get("width", 5)},
            ))
            fig.add_trace(go.Cone(
                x=[endpoint[0]], y=[endpoint[1]], z=[endpoint[2]],
                u=[direction[0]], v=[direction[1]], w=[direction[2]],
                anchor="tip", sizemode="absolute", sizeref=0.06 * length,
                colorscale=[[0, color], [1, color]], showscale=False,
                name=f"{name} arrowhead", legendgroup=group,
                showlegend=False, hoverinfo="skip",
            ))

    # --------------------------------------------------
    # 4. Layout
    # --------------------------------------------------
    # Equal physical axis ranges prevent nearly planar trajectories from
    # producing enormous x/y scene dimensions under aspectmode="data".
    plotted_points = []
    for trace in fig.data:
        xyz = [np.asarray(getattr(trace, axis), dtype=float).ravel()
               for axis in "xyz"]
        points = np.column_stack(xyz)
        plotted_points.append(points[np.all(np.isfinite(points), axis=1)])
    auto_distance = max(3.0, 3.0 * (height - 50) / 800)
    if camera_distance is None:
        camera_distance = auto_distance
    if not np.isfinite(camera_distance) or camera_distance <= 0:
        raise ValueError("camera_distance must be positive and finite")
    zoom_scale = camera_distance / auto_distance if projection == "ortho" else 1.0
    axis_ranges = {}
    if plotted_points and any(len(p) for p in plotted_points):
        points = np.concatenate(plotted_points)
        low, high = points.min(axis=0), points.max(axis=0)
        center = (low + high) / 2
        half_span = max(float(np.max(high - low)) / 2, 1e-9) * 1.10 * zoom_scale
        axis_ranges = {
            f"{axis}axis": {"range": [c - half_span, c + half_span]}
            for axis, c in zip("xyz", center)
        }
    fig.update_layout(
        title=title,
        scene={
            "xaxis_title": f"X [{units}]",
            "yaxis_title": f"Y [{units}]",
            "zaxis_title": f"Z [{units}]",
            "aspectmode": "cube",
            **axis_ranges,
            "camera": _plotly_camera(
                np.rad2deg(np.arctan(1 / np.sqrt(2))) if elev is None else elev,
                45 if azim is None else azim,
                projection, auto_distance if projection == "ortho" else camera_distance,
            ),
        },
        template="plotly_white",
        legend={"x": 0.02, "y": 0.98, "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0},
        height=height,
        margin={"l": 0, "r": 0, "b": 0, "t": 50}
    )

    if show:
        fig.show()

    return fig

def plot_earth_departure(
    v_inf_eci,
    launch_lat_deg,
    launch_lon_deg,
    alpha_launch=None,
    earth_radius_km=R_EARTH,
    vector_display_km=12000.0,
    show=True,
    traces=None,
    t_arrs=None,
    labels=None,
    backend="plotly",
    orbit_color="#ffff00",
    renderer=None,
    elev=np.rad2deg(np.arctan(1 / np.sqrt(2))),
    azim=45,
    projection="ortho",
    camera_distance=None,
):
    """Plot Earth-centered departure geometry in the ECI frame.

    ``v_inf_eci`` is drawn from Earth's center and is scaled only for
    display. ``alpha_launch`` is the inertial right ascension of the launch
    site's radius at launch; if omitted, the supplied longitude is used.
    Optional ``traces`` (N, 3), ``t_arrs``, and ``labels`` are passed to
    ``plot_3d``; orbit positions must be Earth-centered ECI in km.
    The launch azimuth arrow is the local horizontal projection of the
    departure asymptote, with beta measured clockwise from local north.
    Set backend="matplotlib" for a static figure, or renderer="png"
    for PDF-friendly Plotly output (requires Kaleido and Chrome).
    Both backends accept ``elev`` and ``azim`` in degrees, and
    ``projection`` ("ortho" or "persp"); defaults give a +x/+y/+z isometric view.
    ``camera_distance`` controls Plotly camera distance in scene units.
    ``orbit_color`` sets the trajectory color for both backends (default bright yellow).
    """
    if backend not in ("plotly", "matplotlib"):
        raise ValueError("backend must be 'plotly' or 'matplotlib'")
    lat = np.deg2rad(launch_lat_deg)
    lon = np.deg2rad(
        launch_lon_deg if alpha_launch is None else alpha_launch * RAD_TO_DEG
    )

    r_hat = np.array([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat),
    ])
    east_hat = np.array([-np.sin(lon), np.cos(lon), 0.0])
    north_hat = np.array([
        -np.sin(lat) * np.cos(lon),
        -np.sin(lat) * np.sin(lon),
        np.cos(lat),
    ])
    r_launch = earth_radius_km * r_hat

    vectors = [
        {"direction": r_hat, "length": 1.15 * earth_radius_km,
         "color": "crimson", "name": "Launch radius", "width": 4},
    ]
    for direction, color, name in [
        (r_hat, "blue", "Local up"),
        (east_hat, "green", "Local east"),
        (north_hat, "red", "Local north"),
    ]:
        vectors.append({
            "origin": r_launch, "direction": direction,
            "length": 0.60 * earth_radius_km,
            "color": color, "name": name, "width": 4,
        })
    v_inf = np.asarray(v_inf_eci, dtype=float).reshape(3)
    vectors.append({
        "direction": v_inf,
        "length": vector_display_km, "color": "firebrick",
        "name": "Departure asymptote", "width": 7,
    })
    v_norm = np.linalg.norm(v_inf)
    if not np.isfinite(v_norm) or v_norm == 0:
        raise ValueError("v_inf_eci must be finite and nonzero")
    v_hat = v_inf / v_norm
    horizontal = v_hat - np.dot(v_hat, r_hat) * r_hat
    if np.linalg.norm(horizontal) > 1e-12:
        beta = np.arctan2(horizontal @ east_hat, horizontal @ north_hat)
        beta_deg = np.rad2deg(beta) % 360
        vectors.append({
            "origin": r_launch, "direction": horizontal,
            "length": 0.85 * earth_radius_km, "color": "deepskyblue",
            "name": f"Launch azimuth β = {beta_deg:.3f}°", "width": 7,
        })
    fig = plot_3d(
        traces=traces, t_arrs=t_arrs, labels=labels, vectors=vectors,
        trace_colors=orbit_color,
        bodies={"name": "Earth", "radius": earth_radius_km,
                "color": "#4f81bd", "opacity": 0.75},
        title="Earth-centered departure geometry", show=False,
        elev=elev, azim=azim, projection=projection,
        camera_distance=camera_distance,
    )

    fig.add_trace(go.Scatter3d(
        x=[r_launch[0]], y=[r_launch[1]], z=[r_launch[2]],
        mode="markers+text", text=["launch site"], textposition="top center",
        marker={"size": 6, "color": "crimson"}, name="Launch site"
    ))
    fig.update_layout(scene={
        "xaxis_title": "ECI x [km]", "yaxis_title": "ECI y [km]",
        "zaxis_title": "ECI z [km]", "aspectmode": "data",
    })
    if backend == "matplotlib":
        return _matplotlib_3d(
            fig, show=show, elev=elev, azim=azim, projection=projection,
        )
    if show:
        fig.show(renderer=renderer)
    return fig


def plot_flybys(flybys: list[OrbitalFlyby], xlim = None, ylim = None):

    colors = {
        2: "orange",      # Venus
        3: "royalblue",   # Earth
        5: "brown",       # Jupiter
        None: "green"     # Gaspra
    }

    fig, ax = plt.subplots(figsize=(9, 9))

    # Plot Sun
    ax.scatter(0, 0, color="gold", marker="o", s=100, label="Sun", zorder=5)

    # Plot waypoints
    for flyby in flybys:
        
        r = flyby.r_HCI / AU_TO_KM
        ax.scatter(r[0], r[1], color=colors[flyby.planet_num], s=40, zorder=3)
        
        # Dumb dub dumb
        name = flyby.name
        if "Venus" in name:
            ax.annotate(name, (r[0], r[1]),xytext=(-75, 6),textcoords="offset points",fontsize=9)
        elif "Earth Swingby" not in name:
            ax.annotate(name, (r[0], r[1]),xytext=(6, 6),textcoords="offset points",fontsize=9)
        elif "#1" in name:
            ax.annotate("Earth Swingbys", (r[0], r[1]),xytext=(6, 6),textcoords="offset points",fontsize=9)

    ax.set_xlabel("Heliocentric X [AU]")
    ax.set_ylabel("Heliocentric Y [AU]")
    ax.set_title("Galileo Mission Waypoints")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    ax.legend()

    plt.tight_layout()

def plot_hyperbolic_characteristics(flyby: OrbitalFlyby, color: str):
    r = flyby.r_HCI[:2] / AU_TO_KM

    scale = 0.2 / 40  # AU per (km/s)

    v_in = flyby.v_arrival_HCI[:2] * scale
    v_out = flyby.v_departure_HCI[:2] * scale

    plt.arrow(*(r - v_in), *v_in,
              width=0.005, color=color)

    plt.arrow(*r, *v_out,
              width=0.005, color=color)
###########################################################################
#                   Examples
###########################################################################

# if __name__ == "__main__":
#     plot_3d(
#         r_arr,
#         t_arrs=t_arr,
#         labels="Satellite",
#         bodies={"name": "Earth", "radius": R_EARTH},
#         title="Earth Orbit"
#     )
    
#     plot_3d(
#         [r1, r2, r3],
#         t_arrs=t_arr,
#         labels=["Trajectory 1", "Trajectory 2", "Trajectory 3"],
#         bodies={
#             "name": "Pluto",
#             "radius": R_PLUTO,
#             "color": "slategrey"
#         },
#         show_start=True,
#         show_end=True
#     )
    
#     plot_3d(
#         r_arr,
#         bodies=[
#             {
#                 "name": "Pluto",
#                 "radius": R_PLUTO,
#                 "color": "slategrey"
#             },
#             {
#                 "name": "Charon",
#                 "radius": R_CHARON,
#                 "center": [r_PLUTO_CHARON, 0, 0],
#                 "color": "lightgrey"
#             }
#         ]
#     )
    
#     fig = plot_3d(
#         relative_positions,
#         labels="Deputy",
#         title="HCW Relative Motion",
#         show_start=True,
#         show=False
#     )

#     fig.update_layout(scene_camera={
#         "eye": {"x": 0.5, "y": 0.5, "z": 2}
#     ))

#     fig.show()
