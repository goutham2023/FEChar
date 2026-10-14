# FEChAR: Governing Equations

FEChAR is a 1D thermo-chemical ablation model for a charring carbon–phenolic ablator (TACOT). The material pyrolyzes, the pyrolysis gas flows through the pores toward the heated face, and the surface recedes by thermochemical ablation. Only the main equations are listed here.

## 1. In-depth response

**Gas mass conservation + Darcy flow** (pressure equation)

```math
\frac{\partial}{\partial t}\left(\frac{\phi P}{R T}\right) = \frac{\partial}{\partial x}\left(\frac{K_p P}{\mu \phi R T}\frac{\partial P}{\partial x}\right) + (\rho_v-\rho_c)\frac{\partial \alpha}{\partial t}
```

**Energy conservation**

```math
\rho c_p \frac{\partial T}{\partial t} = \frac{\partial}{\partial x}\left(k \frac{\partial T}{\partial x}\right) + \frac{\partial}{\partial x}\left(\dot{m}_g h_g\right) + (h_g-\bar{h})\frac{\partial \rho}{\partial t}
```

**Pyrolysis kinetics** (three-component nth-order Arrhenius)

```math
\frac{\partial \alpha}{\partial t} = \sum_i x_i \frac{\partial \alpha_i}{\partial t}, \qquad \frac{\partial \alpha_i}{\partial t} = B_i \exp\left(-\frac{E_{a,i}}{R T}\right)(1-\alpha_i)^{n_i}
```

## 2. Surface thermochemistry

**Surface energy balance**

```math
\rho_e u_e C_H \left[ H_e - (1+B')\,h_w + B'_c h_c + B'_g h_g \right] + \alpha_w q_{rad} - \epsilon_w \sigma T_w^4 - q_{cond} = 0
```

**Blowing parameters**

```math
B'_g = \frac{\dot{m}_g}{\rho_e u_e C_M}, \qquad B'_c = \frac{\dot{m}_c}{\rho_e u_e C_M}, \qquad B' = B'_g + B'_c
```

**Elemental conservation at the wall** (for each element k, with C_M = C_H)

```math
Y_{k,e} + B'_g Y_{k,g} + B'_c Y_{k,c} = (1+B')\,Y_{k,w}
```

**Blowing correction to the Stanton number**

```math
\frac{C_H}{C_{H0}} = \frac{e^{\zeta}-1}{\zeta}, \qquad \zeta = \frac{2\lambda\,(\dot{m}_g+\dot{m}_c)}{\rho_e u_e C_{H0}}
```

**Surface recession**

```math
\dot{s} = \frac{\dot{m}_c}{\rho_c} = \frac{B'_c \, \rho_e u_e C_M}{\rho_c}
```

The atmosphere is set through its elemental composition at the boundary-layer edge, with Y_C + Y_N + Y_O = 1. The pyrolysis-gas composition is Y_C = 0.206, Y_H = 0.679, Y_O = 0.115.

## 3. Numerical method

- **Space:** linear (P1) finite elements in FreeFEM++, mesh graded toward the heated surface.
- **Time:** second-order backward difference (BDF2):

```math
\left.\frac{\partial \phi}{\partial t}\right|_n \approx \frac{1}{\Delta t}\left(\frac{3}{2}\phi_n - 2\phi_{n-1} + \frac{1}{2}\phi_{n-2}\right)
```

- **Coupling:** pressure, surface thermochemistry/blowing, and temperature are iterated within each time step until converged.
- **Moving boundary:** the mesh follows the receding surface and fields are re-interpolated after each update.

## 4. Nomenclature

| Symbol | Meaning |
|---|---|
| φ, K_p, μ | porosity, permeability, gas viscosity |
| P, T, R | gas pressure, temperature, specific gas constant |
| α | extent of pyrolysis (0 to 1) |
| ρ_v, ρ_c | virgin and char density |
| ṁ_g, ṁ_c | pyrolysis-gas and char mass flux |
| h_g, h_c, h_w, H_e | gas, char, wall, and edge total enthalpy |
| B', B'_g, B'_c | total, gas, and char blowing parameters |
| C_H, C_M | heat- and mass-transfer Stanton numbers |
| Y_k | elemental mass fraction (e = edge, g = gas, c = char, w = wall) |
| ṡ | surface recession rate |

## 5. Limitations

1D through-thickness only, Darcy gas transport, equilibrium surface chemistry, and no mechanical response (stress, cracking, spallation).
