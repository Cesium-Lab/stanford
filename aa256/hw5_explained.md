# AA 256 HW5: How It Was Done

Code: `hw5.m` · Published output: `html/hw5.pdf` · Method source: **course reader, Chapter 2 (§2.2)**

## Final answers

| Quantity | Value |
|---|---|
| Flange A11 [0/0/0] | 4.894 × 10⁵ lbf/in |
| Web A11 [−45/45/45/−45] | 2.026 × 10⁵ lbf/in |
| Flange D11 | 17.98 lbf·in |
| Neutral axis | mid-height of the section (0.521 in from the bottom face) |
| EI_eff (I-beam) | 3.995 × 10⁵ lbf·in² |
| w_max (I-beam, midspan) | **0.00901 in** downward |
| Q̄11 of a ±25° ply | 1.640 × 10⁷ psi |
| EI tube at x = 0 / x = L | 1.557 × 10⁷ / 1.383 × 10⁶ lbf·in² |
| Tube free-end deflection | **1.114 in** downward |

---

## Background you already have (HW1–3)

Everything starts from things you've done before:

1. **Ply stiffness Q** (in material axes, plane stress):
   ν21 = ν12·E2/E1 = 0.0157, and
   Q11 = E1/(1−ν12ν21) = 23.30 Msi, Q22 = 1.306 Msi, Q12 = ν12·Q22 = 0.366 Msi, Q66 = G12 = 0.90 Msi.
2. **Rotate to the beam axis:** Q̄ = T⁻¹ Q T⁻ᵀ. This is the same `T` function and `Tk \ Q / Tk'` line from hw3/hw4.
3. **ABD matrices:** A = Σ Q̄ₖ(zₖ−zₖ₋₁), B = ½ Σ Q̄ₖ(zₖ²−zₖ₋₁²), D = ⅓ Σ Q̄ₖ(zₖ³−zₖ₋₁³).

The `laminate()` function in `hw5.m` is a stripped-down version of your `laminate_matrices.m`.

What's **new** in HW5 is going from a *plate* (a stiffness per unit width, A and D) to a *beam* (one number, EI). Engineers often call that "smearing." The rule from the course reader is:

> Treat each wall of the cross-section as its own laminate strip. Each strip carries axial stress σ₁ = Q̄11·(strain). Integrate σ₁·z over the whole cross-section to get the moment M = EI·κ.

The reader uses the **plane-strain** form (Q̄11, A11, D11) for every derivation and notes that plane stress just swaps Q̄11 → 1/S̄11. Both problems below follow the reader and use Q̄11/A11/D11.

---

## Problem 1: Composite I-beam

### Geometry
- Flange: 3 plies × 0.007 in, so t_f = **0.021 in**, width b = 1.5 in
- Web: 4 plies × 0.007 in, so t_w = **0.028 in**, clear height h_w = 1.0 in
- Span L = **12 in**. The 15 in overall length is a distractor.

### (a) A11, D11, and why B = 0

**Flange [0/0/0]:** every ply is at 0°, so Q̄11 = Q11 = 23.30 Msi.
- A11 = Q11·t_f = 23.30×10⁶ × 0.021 = **4.894 × 10⁵ lbf/in**
- D11 = Q11·t_f³/12 = 23.30×10⁶ × 0.021³/12 = **17.98 lbf·in**

**Web [−45/45/45/−45]:** at ±45°,
Q̄11 = Q11·c⁴ + 2(Q12 + 2Q66)·s²c² + Q22·s⁴ = ¼(Q11 + 2Q12 + 4Q66 + Q22) = 7.235 Msi.
The sign of the angle doesn't matter for Q̄11, so every ply has the same value.
- A11 = 7.235×10⁶ × 0.028 = **2.026 × 10⁵ lbf/in**

That's only about 30% of the flange's per-thickness stiffness: ±45 plies are weak axially. They exist to carry shear.

**Why B = 0:** B = ½ Σ Q̄ₖ(zₖ² − zₖ₋₁²). Both laminates are **symmetric about their own mid-plane**: [0/0/0] trivially, and [−45/45 | 45/−45] mirrors. A ply at +z and its mirror twin at −z have the same Q̄ and contribute equal and opposite amounts to B, so the sum cancels exactly. MATLAB confirms B = 0 for the flange and ~10⁻²⁰ (round-off) for the web.

### (b) Neutral axis and EI_eff

**Neutral axis.** The neutral axis is where the net axial force from pure bending is zero, i.e. the stiffness-weighted centroid:

  z_NA = Σ(A11ᵢ·widthᵢ·zᵢ) / Σ(A11ᵢ·widthᵢ)

Three things make this trivial:
1. Each laminate is symmetric (B11 = 0), so each strip's own neutral plane is its mid-plane. This is reader Eq. 2.30: d₀ = B11/A11 = 0.
2. The two flanges are identical and placed symmetrically.
3. The web is centered.

So **the neutral axis is at mid-height of the web**, 0.521 in from the bottom face of the 1.042 in deep section. The code computes the weighted centroid explicitly to show this.

**EI_eff derivation** (reader Eqs. 2.31–2.41). Split the moment into three strip contributions:

  M = ∫σ₁ z dA = (M)_top flange + (M)_web + (M)_bottom flange

*Each flange:* the strip sits a distance H/2 from the neutral axis, where H = distance between the flange mid-planes = h_w + t_f = **1.021 in**. Integrating Q̄11·(z κ)·z over the flange, with z measured from the neutral axis, gives:

  (M)_flange = b·[D11 + (H/2)²·A11]·κ    (B11 = 0 kills the cross term)

This is the **composite parallel-axis theorem**. D11 plays the role of "EI about its own centroid" and A11·(H/2)² is the "EA·d²" transfer term.

*Web:* it's a vertical strip of height h_w, centered on the neutral axis. Its fibers sit at heights z from −h_w/2 to +h_w/2, and its in-plane axial stiffness per unit height is A11_w:

  (M)_web = ∫ A11_w · z² dz · κ = A11_w · h_w³/12 · κ

This is the composite version of "E·t·h³/12".

*Total:*

  **EI_eff = 2·b·[D11 + (H/2)²·A11_f] + A11_w·h_w³/12**

| Term | Value (lbf·in²) | Share |
|---|---|---|
| 2·b·D11 (flanges bending about their own mid-plane) | 54 | ~0.01% |
| 2·b·(H/2)²·A11 (flanges, parallel-axis term) | 3.826 × 10⁵ | 95.8% |
| A11_w·h_w³/12 (web) | 1.688 × 10⁴ | 4.2% |
| **EI_eff** | **3.995 × 10⁵** | |

**Takeaway:** an I-beam works by putting stiff 0° material far from the neutral axis. The flanges' own D11 is negligible, and the ±45 web hardly contributes to bending (it's there for shear).

### (c) Midspan deflection

Simply supported beam, central load:

  w_max = P·L³ / (48·EI_eff) = 100 × 12³ / (48 × 3.995×10⁵) = **0.00901 in** (downward)

---

## Problem 2: Tapered elliptical tube

### Setup
- Cantilever with length L = 42 in, fixed at x = 0, load P = 400 lbf downward at x = L.
- Layup [25/−25]s, 4 plies × 0.007 in, so the wall is 0.028 in thick.
- Outer semi-axes: vertical a(x) = 2 − x/L, horizontal b(x) = 3 − 2x/L.

### Step 1: Ply stiffness

Reader Eq. 2.48: the tube's bending rigidity is the **sum over plies of Q̄11ᵢ × Iᵢ**, where Iᵢ is that ply's own moment of inertia about the bending axis. Since Q̄11 doesn't care about the sign of the angle, all four plies have

  Q̄11(±25°) = **1.640 × 10⁷ psi**

(For comparison, a 0° ply is 2.33 × 10⁷ psi.)

The reader also notes that B_x = 0 for tubes *regardless* of layup. The wall wraps all the way around, so coupling terms cancel.

### Step 2: Each ply as an elliptical annulus

A solid ellipse bending about its horizontal axis (bending in the vertical direction, semi-axis a) has I = (π/4)·a³·b.

Each ply is the region between two ellipses. Going **from the outside in**, ply j (j = 0 for the outermost) has:
- outer semi-axes (a − j·t, b − j·t)
- inner semi-axes (a − (j+1)·t, b − (j+1)·t)

so

  I_ply = (π/4)·[ (a−j t)³(b−j t) − (a−(j+1)t)³(b−(j+1)t) ]

and

  **EI(x) = Σ over 4 plies of Q̄11 · I_ply(x)**

That's `EI_section()` in the code. EI drops from **1.557 × 10⁷** at the root to **1.383 × 10⁶ lbf·in²** at the tip, a factor of 11, because I scales roughly as a²·(a+3b)·t.

*Sanity check:* the thin-wall ellipse formula I ≈ (π/4)·a²·t·(a + 3b), evaluated at the root with the mid-wall a, b, gives ≈ 1.56 × 10⁷, matching the code.

### Step 3: Integrate curvature

Moment from the tip load: M(x) = −P·(L − x). It's hogging, and largest at the wall.

Curvature: κ(x) = w''(x) = M(x)/EI(x)

Boundary conditions at the fixed end: w(0) = 0 and w'(0) = 0.

Integrate twice:
- slope: θ(x) = ∫₀ˣ κ dx
- deflection: w(x) = ∫₀ˣ θ dx

The code does this with `cumtrapz` on 2001 points. As an independent check it also uses the closed form from the unit-load method or moment-area method:

  w(L) = −∫₀ᴸ P·(L−x)² / EI(x) dx

evaluated with MATLAB's adaptive `integral`. Both give **−1.11382 in**.

**Free-end deflection = 1.114 in downward.**

### Is that number reasonable?

- If the whole tube had the stiff root EI: PL³/3EI = 0.63 in
- If the whole tube had the floppy tip EI: PL³/3EI = 7.14 in

1.11 in sits between those bounds, closer to the stiff end. That makes sense: the moment is biggest near the root, which is exactly where the tube is stiffest. The curvature plot in the PDF peaks around x ≈ 25 in, where the falling moment and falling stiffness balance.

---

## Judgment calls (worth knowing if you're asked)

1. **Plane strain (Q̄11, A11, D11) vs plane stress (1/S̄11, 1/a11, 1/d11).** The reader derives everything with Q̄11 and says so explicitly, and HW part (a) asks for A11/D11, so that's what's used. It notes that for angle plies the two can differ a lot. For the ±45 web, 1/S̄11 is about 3× smaller than Q̄11, but the web is only 4% of EI, so the I-beam answer barely moves. For the ±25 tube the difference would matter more.
2. **Tube geometry.** The problem text says a(x), b(x) are the **outer** semi-axes and the plies step inward. The figure caption says "a, b to laminate mid-surface." I followed the text. Using the mid-surface instead would stiffen the tube by a few percent (≈2% at the root, ≈4% at the tip).
3. **I-beam H.** H = h_w + t_f is the distance between the flange *mid-planes*, because the reader's flange integral is written about each flange's own mid-plane (that's why B11 = 0 drops out). The web uses only the clear height h_w = 1.0 in ("ignore overlaps").

---

## Cram sheet: concepts to actually learn

- **A11** = axial stiffness per unit width (lbf/in). **D11** = bending stiffness per unit width (lbf·in). **B** = stretch–bend coupling, which is zero for symmetric layups.
- **Plate → beam:** a flange strip contributes width × (D11 + d²·A11). A vertical web strip contributes A11·h³/12. This is the parallel-axis theorem with A11 in place of E·t.
- **Neutral axis** = stiffness-weighted centroid, Σ(A11·w·z)/Σ(A11·w), not the geometric centroid. It shifts if the flanges differ or a laminate is unsymmetric (d₀ = B11/A11).
- **Tubes:** EI = Σ Q̄11ᵢ·Iᵢ, ply by ply. Coupling is always zero.
- **Variable EI beam:** you can't use PL³/3EI. Integrate κ = M/EI twice with the boundary conditions, or use w_tip = ∫ M·m/EI dx, where m is the moment from a unit load at the tip.
- **Angle-ply intuition:** Q̄11 falls quickly as ply angle grows (0°: 23.3, 25°: 16.4, 45°: 7.2 Msi). Flanges get 0° plies for bending and webs get ±45° plies for shear.
