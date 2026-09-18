# FECHAR theory: governing equations and numerical scheme

This document explains **what** FECHAR solves and **how**, so that someone
who has never seen the code can read `main.edp` and understand the physical
model and numerical treatment. The governing-equation formulation described
here follows the thermo-chemical ablation model used for the carbon–phenolic
ablator, including in-depth gas transport and pyrolysis, surface
thermochemistry, atmospheric-composition effects, and surface recession.

If you just want to run it, see the top-level [README](../README.md). If
you're comparing FECHAR against another ablative-material-response solver,
this is the page to check for the physical terms represented in the model.

## 1. Physical picture

A charring carbon–phenolic ablator is a porous composite exposed on one face
to a hot gas flow. As it heats up:

1. The resin constituents **pyrolyze** (thermally decompose), converting
   solid mass into pyrolysis gas and leaving behind lower-density char.
2. The pyrolysis gas **percolates** through the porous char/virgin material
   toward the heated surface.
3. At the surface, the char interacts with the external atmosphere and is
   removed through thermochemical ablation, causing the surface to **recede**.
4. The injected pyrolysis gas and surface-generated char gases modify the
   boundary layer through **blowing**, reducing the convective heat transfer
   to the surface.

FECHAR models these processes in 1D through the material thickness. The
in-depth response is governed by coupled mass transport, energy conservation,
pyrolysis kinetics, and Darcy flow of the pyrolysis gas. The exposed surface
is coupled to a chemically reacting boundary layer through a surface energy
balance and elemental conservation.

```text
   heated / ablating face                          back face
          x = 0  ─────────────────────────────────────►  x = L
          │                                                  │
          │       char       pyrolyzing / transition  virgin │
          │◄────────────►◄──────────────────────────►◄──────►│
          │                                                  │
      gas flows toward the surface              fixed boundary
      surface recedes at rate ṡ
```

The mesh is graded toward the exposed surface because the strongest thermal
and chemical gradients occur there. Surface recession is accounted for by
moving the computational boundary inward.

---

## 2. Governing equations

The internal thermo-chemical response of the porous carbon–phenolic ablative
medium is modeled using coupled mass transport and energy conservation,
with pyrolysis kinetics providing the decomposition source terms.

### 2.1 Gas mass-transport equation

The gas-phase pressure distribution inside the porous decomposing material is
governed by the combined gas mass-conservation and Darcy-flow equation:

\[
\frac{\partial}{\partial t}
\left(
\frac{\phi P}{RT}
\right)
=
\nabla\cdot
\left(
\frac{K_p P}{\mu \phi RT}\nabla P
\right)
+
(\rho_v-\rho_c)\frac{\partial\alpha}{\partial t}.
\tag{1}
\]

Here, \(\phi\) is the porosity, \(K_p\) is the isotropic permeability,
\(\mu\) is the dynamic gas viscosity, \(R\) is the effective specific gas
constant, and \(P\) is the gas pressure. The variable \(\alpha\in[0,1]\)
denotes the local extent of pyrolysis.

The source term

\[
(\rho_v-\rho_c)\frac{\partial\alpha}{\partial t}
\]

represents the generation of gas associated with solid decomposition, where
\(\rho_v\) and \(\rho_c\) are the virgin and char densities, respectively.

For the 1D through-thickness implementation, the spatial divergence reduces
to the corresponding derivative in \(x\).

The pyrolysis-gas mass flux is obtained from Darcy's law and is subsequently
used in the energy equation and in the surface blowing calculation.

### 2.2 In-depth energy equation

The transient thermal response of the degrading material is governed by

\[
\rho c_p\frac{\partial T}{\partial t}
=
\nabla\cdot(k\nabla T)
+
\nabla\cdot(\dot{\mathbf m}_g h_g)
+
(h_g-\bar h)\frac{\partial\rho}{\partial t}.
\tag{2}
\]

The first term on the right-hand side represents heat conduction through the
porous material. The second term represents enthalpy transport by the
pyrolysis gas. The final term accounts for the enthalpy exchange associated
with conversion of solid material into gas.

The effective bulk volumetric heat capacity \(\rho c_p\) and thermal
conductivity \(k\) vary with the state of decomposition. The pyrolysis-gas
mass-flux vector is \(\dot{\mathbf m}_g\), \(h_g\) is the specific enthalpy
of the pyrolysis gas, and \(\bar h\) is the mixture enthalpy.

For the 1D model, the energy equation is solved through the material
thickness using the corresponding \(x\)-direction fluxes.

### 2.3 Pyrolysis kinetics closure

The overall extent of pyrolysis appearing in Eqs. (1) and (2) is obtained by
combining the individual decomposition reactions:

\[
\frac{\partial\alpha}{\partial t}
=
\sum_i x_i\frac{\partial\alpha_i}{\partial t},
\qquad
\sum_i x_i=1.
\tag{3}
\]

Here, \(\alpha_i\) is the local extent of reaction of constituent \(i\), and
\(x_i\) is its mass-loss factor, representing its fractional contribution to
the total mass loss.

Each constituent decomposition reaction is described using an
nth-order Arrhenius law,

\[
\frac{\partial\alpha_i}{\partial t}
=
B_i
\exp\left(
-\frac{E_{a,i}}{RT}
\right)
(1-\alpha_i)^{n_i}.
\tag{4}
\]

Here, \(B_i\) is the pre-exponential factor, \(E_{a,i}\) is the activation
energy, and \(n_i\) is the reaction order for constituent \(i\).

The model uses a three-component decomposition representation for the
carbon–phenolic composite, with the individual reaction rates providing the
state-dependent decomposition rate used in the gas-generation and thermal
response calculations.

As decomposition proceeds, the local material density, porosity,
permeability, thermal conductivity, and heat capacity evolve with the
decomposition state.

---

## 3. Surface thermochemistry and boundary conditions

At the material–gas interface, the wall temperature \(T_w\) and surface
recession rate \(\dot s\) are coupled to the external flight environment.
The surface is closed through a nonlinear surface energy balance.

### 3.1 General surface energy balance

The surface energy balance is

\[
q''_{\mathrm{conv,bl}}
+
\alpha_w q''_{\mathrm{rad}}
-
\epsilon_w\sigma T_w^4
-
(\rho_v)_w h_w
+
\dot m''_c h_c
+
\dot m''_g h_g
-
q''_{\mathrm{cond}}
=
0.
\tag{5}
\]

Here:

- \(q''_{\mathrm{conv,bl}}\) is the convective heat flux delivered by the
  boundary layer;
- \(q''_{\mathrm{rad}}\) is the incident radiative heat flux;
- \(\alpha_w\) is the wall absorptivity;
- \(\epsilon_w\) is the wall emissivity;
- \(\sigma\) is the Stefan–Boltzmann constant;
- \(q''_{\mathrm{cond}}\) is the conductive heat flux into the material;
- \((\rho_v)_w h_w\) represents the enthalpy carried away by the net mass
  blown from the surface;
- \(\dot m''_c h_c\) is the enthalpy flux associated with char removal; and
- \(\dot m''_g h_g\) is the enthalpy flux associated with pyrolysis-gas
  injection.

The surface thermochemistry and boundary-layer quantities are coupled
iteratively because the wall state, gas blowing, char removal, and heat
transfer depend on one another.

### 3.2 Boundary-layer blowing parameters

The non-dimensional pyrolysis-gas, char, and total blowing rates are defined
as

\[
B'_g
=
\frac{\dot m''_g}
{\rho_e u_e C_M},
\tag{6a}
\]

\[
B'_c
=
\frac{\dot m''_c}
{\rho_e u_e C_M},
\tag{6b}
\]

and

\[
B'=B'_g+B'_c.
\tag{6c}
\]

Here, \(\rho_e\) and \(u_e\) are the density and velocity at the
boundary-layer edge, and \(C_M\) is the mass-transfer Stanton number.

The pyrolysis-gas blowing parameter is determined by the in-depth
pyrolysis-gas mass flux, while the char blowing parameter represents mass
removed from the surface through ablation.

### 3.3 Elemental conservation at the ablating surface

The external atmospheric composition is supplied through the elemental
composition at the boundary-layer edge. Under the assumption of chemical
equilibrium at the wall and a unity Lewis number,

\[
C_M=C_H.
\]

For each element \(k\), elemental conservation at the surface requires

\[
Y_{k,e}
+
B'_gY_{k,g}
+
B'_cY_{k,c}
=
(1+B')Y_{k,w}.
\tag{7}
\]

Here:

- \(Y_{k,e}\) is the mass fraction of element \(k\) at the
  boundary-layer edge;
- \(Y_{k,g}\) is the mass fraction of element \(k\) in the pyrolysis gas;
- \(Y_{k,c}\) is the mass fraction of element \(k\) in the char contribution;
  and
- \(Y_{k,w}\) is the mass fraction of element \(k\) in the wall-equilibrium
  state.

This relation provides the surface chemical closure while allowing the
external atmospheric elemental composition to vary.

### 3.4 Reduced surface energy equation

With the boundary-layer assumptions above, the general surface energy
balance can be written in the standard boundary-layer form

\[
\rho_eu_eC_H
\left[
H_e-h_w
+
B'_c h_c
+
B'_g h_g
-
B'h_w
\right]
+
\alpha_w q''_{\mathrm{rad}}
-
\epsilon_w\sigma T_w^4
-
q''_{\mathrm{cond}}
=
0.
\tag{8}
\]

Equivalently, the terms in the square brackets can be grouped as

\[
H_e-(1+B')h_w+B'_c h_c+B'_g h_g.
\]

Here, \(H_e\) is the boundary-layer-edge total enthalpy and \(C_H\) is the
heat-transfer Stanton number for the non-blowing reference state.

The wall enthalpy \(h_w\) and the char/gas thermochemical state are obtained
from the surface thermochemistry calculation. In the present formulation,
the wall-equilibrium state is evaluated with the thermochemical surface
model, allowing the external elemental composition to be changed directly
rather than requiring a separate material-response calculation for every
atmosphere.

### 3.5 Blowing correction to the heat-transfer Stanton number

The reduction in heat transfer caused by pyrolysis-gas and char injection is
included through a blowing correction to the heat-transfer Stanton number:

\[
\frac{C_H}{C_{H0}}
=
\frac{e^\zeta-1}{\zeta},
\qquad
\zeta=
\frac{2\lambda
\left(\dot m''_g+\dot m''_c\right)}
{\rho_eu_eC_{H0}}.
\tag{9}
\]

Here, \(C_{H0}\) is the zero-blowing Stanton number and \(\lambda\) is the
blowing-correction coefficient.

The total injected/removing mass flux therefore affects the surface heat
transfer through the blowing correction, while the individual gas and char
contributions enter the surface energy and elemental balances separately.

---

## 4. Surface recession

The surface recession is determined from the char mass-removal rate. The
recession velocity is related to the char blowing parameter through

\[
\dot s
=
\frac{B'_c\rho_e}{\rho_c},
\]

where \(\rho_c\) is the char density.

The instantaneous material surface is therefore displaced as ablation
proceeds. The computational domain is updated to follow this receding
surface.

---

## 5. Atmospheric composition and surface chemistry

The external atmosphere is represented by its elemental composition. For the
C–N–O calculations, the atmospheric composition satisfies

\[
Y_C+Y_N+Y_O=1.
\]

Changing these elemental fractions changes the chemical-equilibrium state at
the ablating wall and consequently changes the wall temperature, species
composition, gas/char mass fluxes, and material recession.

The wall-equilibrium calculation considers gas-phase species including
C, H, O, N, CH4, CN, CO, CO2, C2, C2H, C2H2, C3, C4, C4H2, C5, HCN,
H2, H2O, N2, CH2OH, CNN, CNC, CNCOCN, C6H6, and HNC, together with
graphitic carbon, C(gr), in the solid phase.

The pyrolysis-gas elemental composition used in the surface calculation is

\[
Y_C=0.206,\qquad
Y_H=0.679,\qquad
Y_O=0.115.
\]

The external environment can then be varied independently in the C–N–O
composition space while retaining the same ablative material and imposed
heating condition.

---

## 6. Numerical method

The governing equations are discretized in space using linear (P1) finite
elements and integrated in time using a second-order time-advancement
scheme within FreeFEM++.

### 6.1 Spatial discretization

The model is one-dimensional through the material thickness. Linear P1
finite elements are used on the computational mesh, with the mesh biased
toward the exposed surface to resolve the strong thermal and chemical
gradients near the ablating boundary.

### 6.2 Time discretization

The transient in-depth equations are integrated using a second-order
backward-difference formulation. For a generic field \(\phi\),

\[
\left.\frac{\partial\phi}{\partial t}\right|_n
\approx
\frac{1}{\Delta t}
\left(
\frac{3}{2}\phi_n
-2\phi_{n-1}
+\frac{1}{2}\phi_{n-2}
\right).
\]

Thus the coefficients \(1.5\), \(-2\), and \(0.5\) appearing in the
discrete forms correspond to the BDF2 time stencil.

### 6.3 Nonlinear coupling

The thermo-chemical problem is strongly coupled. The pressure, temperature,
decomposition state, gas generation, surface thermochemistry, blowing
parameters, and recession rate depend on one another.

The numerical solution therefore proceeds through iterative sub-steps within
each time step. The gas-pressure field, surface thermochemistry/blowing
calculation, and temperature field are updated until the coupled solution
converges or the prescribed iteration limit is reached.

### 6.4 Moving boundary

Surface recession is handled by moving the computational mesh as the
material surface recedes. The fields are re-interpolated onto the updated
mesh after the surface position changes.

This allows the model to retain a fixed computational representation of the
material thickness relative to the receding surface while accounting for
the physical loss of material.

### 6.5 Thermochemical coupling

The surface calculation is coupled to the thermochemical model to determine
the equilibrium wall state, wall enthalpy, and surface blowing quantities.
The boundary-layer edge elemental composition is supplied according to the
external atmospheric condition.

This coupling is important when comparing different atmospheric
compositions because the surface equilibrium is not independent of the
external environment.

---

## 7. Material data

The default material represented by the model is the TACOT
(Theoretical Ablative Composite for Open Testing) carbon–phenolic-type
ablator. The material properties and decomposition parameters define the
virgin and char states and the evolution of the material during pyrolysis.

The model uses state-dependent material properties so that the thermal and
transport response evolves continuously as the material decomposes.

---

## 8. Model assumptions and limitations

The present formulation is a one-dimensional thermo-chemical ablative
material-response model. The following assumptions and limitations should be
kept in mind:

- The in-depth response is represented in **1D through the material
  thickness**.
- The pyrolysis gas is transported through the porous material using
  **Darcy flow**.
- The decomposition of the material is represented using
  **multi-component Arrhenius kinetics**.
- The surface is treated using a **thermochemical equilibrium formulation**
  coupled to the external boundary layer.
- The surface heat-transfer reduction caused by mass injection/removal is
  represented using a **blowing correction** to the Stanton number.
- Surface radiation is included through the wall radiation terms when the
  radiative contribution is enabled.
- The model does not include mechanical response such as stress,
  cracking, or spallation.
- The present formulation does not resolve multidimensional lateral
  transport effects.
- The in-depth pyrolysis-gas treatment is a mass/energy transport model; the
  detailed atmospheric chemical equilibrium is applied at the material
  surface.

---

## 9. Summary of the coupled model

The FECHAR formulation can be viewed as the following coupled sequence:

```text
             External atmospheric composition
                         │
                         ▼
              Boundary-layer edge state
                         │
                         ▼
               Surface thermochemistry
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Wall equilibrium       Blowing parameters
        (h_w, species)          (B'_g, B'_c)
              │                     │
              └──────────┬──────────┘
                         ▼
                Surface energy balance
                         │
                         ▼
                    Wall T / q''
                         │
                         ▼
              In-depth material response
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Pyrolysis   Gas flow   Heat transfer
          kinetics    (Darcy)    / enthalpy
              │          │          │
              └──────────┼──────────┘
                         ▼
                  Surface mass flux
                         │
                         ▼
                    Recession ṡ
                         │
                         ▼
                    Moving mesh
```

The governing equations are therefore not solved independently: pyrolysis
controls gas generation and material properties; gas transport contributes
to the in-depth energy balance and surface blowing; surface thermochemistry
determines the wall state and char removal; and the resulting recession
updates the computational domain.
