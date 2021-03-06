import matplotlib.pyplot as plt
import modelmiezelb.arg_inel_mieze_model as arg
###############################################################################
from numpy import linspace, tile, trapz, all, isclose, arange, ones
###############################################################################
from modelmiezelb.correction import CorrectionFactor, DetectorEfficiencyCorrectionFactor, EnergyCutOffCorrectionFactor
from modelmiezelb.lineshape import LorentzianLine
from modelmiezelb.sqe_model import SqE, UPPER_INTEGRATION_LIMIT
###############################################################################
from modelmiezelb.utils.util import detector_efficiency, triangle_distribution, energy_from_lambda, energy_lambda_nrange

def test_CorrectionFactor_instantiation():
    corrf1 = CorrectionFactor(None)
    print(f"Instance required calculation parameters {corrf1._required_params}")
    print(f"Class required calculation parameters {CorrectionFactor._required_params}")

#------------------------------------------------------------------------------

def test_DetectorEfficiencyCorrectionFactor():
    # We need some lines
    L1 = LorentzianLine("Lorentzian1", (-5.0, 5.0), x0=0.0, width=0.4, c=0.0, weight=2)
    L2 = LorentzianLine(name="Lorentzian2", domain=(-5.0, 5.0), x0=-1.0, width=0.4, c=0.02, weight=1)
    # Contruct a SqE model
    sqe = SqE(lines=(L1, L2), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    # Instantiate a detector efficiency corr factor
    decf = DetectorEfficiencyCorrectionFactor(sqe)

    n_e = 10
    n_lam = 5
    lam = 6.0 * linspace(1-0.12*1.01, 1+0.12*1.01, n_lam)
    lams = tile(lam, (n_e, 1))
    
    a = -0.99999 * energy_from_lambda(lam)
    b = 15.0 + a
    es = linspace(a, b, n_e)

    deteff = detector_efficiency(es, lams, 1)
    tria = triangle_distribution(lams, 6.0, 0.12)

    print("Triangular wavelenght distr.: ", tria)
    print("Triangular wavelength distr. shape: ", tria.shape)
    print("Det. eff. values: ", deteff)
    print("Det. eff. values shape: :", deteff.shape)

    sqevals = sqe(es)

    print("Manual mult.: ", sqevals * deteff * tria)
    print("Class result: ", decf(es, lams))

    print("Are manual and deteffcorrfac identical?: ", all((sqevals * deteff * tria) == decf(es, lams)))

#------------------------------------------------------------------------------

def test_DetectorEfficiencyCorrectionFactor_compare_with_arg():
    # We need some lines
    L1 = LorentzianLine(name="Lorentzian1", domain=(-16.0, 16.0), x0=-1.0, width=0.4, c=0.0, weight=1)
    # Contruct a SqE model
    sqe = SqE(lines=(L1,), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    # Instantiate a detector efficiency corr factor
    decf = DetectorEfficiencyCorrectionFactor(sqe)

    n_e = 15000
    n_lam = 20
    lam = 6.0 * linspace(1-0.12*1.01, 1+0.12*1.01, n_lam)
    lams = tile(lam, (n_e, 1))
    
    a = -0.99999 * energy_from_lambda(lam)
    b = 15.0 + a
    es = linspace(a, b, n_e)

    test_decf_val = arg.DetFac_Eint_lamInt(
        arg.fqe_I,
        -1.0,
        0.4,
        15000,
        20,
        6.0,
        0.12,
        1,
        0.0,
        1.0,
        20,
        0.5,
        0.00001,
        350.
    )
    decf_val_man_int = decf(es, lams)
    decf_val = decf.correction(es, lams)
    print("arg res: ", test_decf_val)
    print("class calc res manualy integrated: ", decf_val_man_int)
    print("class res: ", decf_val)

#------------------------------------------------------------------------------

def test_EnergyCutOffCorrectionFactor_vs_arg():
    # We need some lines
    L1 = LorentzianLine(name="Lorentzian1", domain=(-16.0, 16.0), x0=-1.0, width=0.4, c=0.0, weight=1)
    # Contruct a SqE model
    sqe = SqE(lines=(L1,), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    # Instantiate a energy cutoff corr factor
    eccf = EnergyCutOffCorrectionFactor(sqe)

    n_e = 15000
    n_lam = 20
    lam = 6.0 * linspace(1-0.12*1.01, 1+0.12*1.01, n_lam)
    lams = tile(lam, (n_e, 1))
    
    a = -0.99999 * energy_from_lambda(lam)
    b = 15.0 + a
    es = linspace(a, b, n_e)

    test_eccf_vals = arg.CutFac_Eint(
        arg.lorentzian,
        -1.0,
        0.4,
        15000,
        20,
        6.0,
        0.12,
        1,
        0.0,
        1.0,
        20,
        0.5,
        0.00001,
        350.
    )

    eccf_vals = eccf.correction(es, lams)

#    print(test_eccf_vals.shape)
    print(test_eccf_vals)

#    print(eccf_vals.shape)  
    print(eccf_vals)
#    print(isclose(eccf_vals, test_eccf_vals, atol=0.01))
    # argsqe = arg.SvqE(arg.lorentzian,
    #     es[::50,0],
    #     -1.0,
    #     0.4,
    #     0.0,
    #     1.0,
    #     6.0,
    #     20,
    #     0.000001,
    #     0.1,
    #     350.)
#    print(argsqe)
#    plt.plot(es[::50,0], sqe(es[::50,0]))
#    plt.plot(es[::50,0], argsqe)
#    plt.show()

#------------------------------------------------------------------------------

def test_correctionFactor_dimensionality():
    # We need some lines
    L1 = LorentzianLine(name="Lorentzian1", domain=(-16.0, 16.0), x0=-1.0, width=0.4, c=0.0, weight=1)
    # Contruct a SqE model
    sqe = SqE(lines=(L1,), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    # Instantiate a detector efficiency corr factor
    decf = DetectorEfficiencyCorrectionFactor(sqe)
    # Instantiate a energy cutoff corr factor
    eccf = EnergyCutOffCorrectionFactor(sqe)

    n_e = 15
    n_lam = 5
    lam = 6.0 * linspace(1-0.12*1.01, 1+0.12*1.01, n_lam)
    lams = tile(lam, (n_e, 1))
    
    a = -0.99999 * energy_from_lambda(lam)
    b = 15.0 + a
    es = linspace(a, b, n_e)

    print(lams)
    print(es)
    print(decf.calc(es, lams))
    print(eccf.calc(es, lams))

#------------------------------------------------------------------------------

def test_EnergyCutoffCorrectionFactor():
    # We need some lines
    L1 = LorentzianLine("Lorentzian1", (-5.0, 5.0), x0=0.0, width=0.4, c=0.0, weight=2)
    L2 = LorentzianLine(name="Lorentzian2", domain=(-5.0, 5.0), x0=-1.0, width=0.4, c=0.02, weight=1)
    # Contruct a SqE model
    sqe = SqE(lines=(L1, L2), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    new_domain = (-1 * energy_from_lambda(6.0), UPPER_INTEGRATION_LIMIT)
    sqe.update_domain(new_domain)
    # init energycutoff
    eccf = EnergyCutOffCorrectionFactor(sqe, n_e=10000, n_lam=20)

    n_e = 10000
    n_lam = 5
    lam = 6.0 * linspace(1-0.12*1.01, 1+0.12*1.01, n_lam)
    lams = tile(lam, (n_e, 1))
    
    a = -0.99999 * energy_from_lambda(lam)
    b = 15.0 + a
    es = linspace(a, b, n_e)

    ### Calculate the trapz integral over the S(q,E)
    # Only over domain (interval length: 15 meV)

    I_over_dom_only = trapz(sqe(es[:, 2]), es[:, 2])
    print("Trapz integration over the domain.")
    print(f"Interval {a[2]:.4f} - {b[2]:.4f} -> length {b[2]-a[2]:.4f} meV.")
    print(f"#Steps = {n_e}")
    print(f"Integral value: {I_over_dom_only:.4f}")
#    plt.plot(es[:,2], sqe(es[:,2]), label="Over domain only")
#    plt.show()

    # Beyond domain same array length
    es_same_length = linspace(-UPPER_INTEGRATION_LIMIT, UPPER_INTEGRATION_LIMIT, n_e)
    I_beyond_dom_same_length = trapz(sqe(es_same_length), es_same_length)
    print("\nTrapz integration beyond the domain with varrying stepsize.")
    print(f"Interval {-UPPER_INTEGRATION_LIMIT} - {UPPER_INTEGRATION_LIMIT} -> length {30.0} meV.")
    print(f"#Steps = {n_e}")
    print(f"Integral value: {I_beyond_dom_same_length:.4f}")
#    plt.plot(es_same_length, sqe(es_same_length), ls="--", label="Beyond domain n_e=10000")
#    plt.show()

    # Beyond domain same step size
    es_same_stepsize = arange(-UPPER_INTEGRATION_LIMIT, UPPER_INTEGRATION_LIMIT+0.001, 15e-3)
    I_beyond_dom_same_stepsize = trapz(sqe(es_same_stepsize), es_same_stepsize)
    print("\nTrapz integration beyond the domain with varrying stepsize.")
    print(f"Interval {-UPPER_INTEGRATION_LIMIT} - {UPPER_INTEGRATION_LIMIT} -> length {30.0} meV.")
    print(f"#Steps = {30.0 / 0.015}")
    print(f"Integral value: {I_beyond_dom_same_stepsize:.4f}")
#    plt.plot(es_same_stepsize, sqe(es_same_stepsize), ls="-.", label="Beyond domain de=0.015 meV")
#    plt.show()

#------------------------------------------------------------------------------
    
def test_DetectorEfficiency_cancel():
    # We need some lines
    L1 = LorentzianLine("Lorentzian1", (-5.0, 5.0), x0=0.0, width=0.4, c=0.0, weight=2)
    L2 = LorentzianLine(name="Lorentzian2", domain=(-5.0, 5.0), x0=-1.0, width=0.4, c=0.02, weight=1)
    # Contruct a SqE model
    sqe = SqE(lines=(L1, L2), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    new_domain = (-1 * energy_from_lambda(6.0), UPPER_INTEGRATION_LIMIT)
    sqe.update_domain(new_domain)
    # init energycutoff
    decf = DetectorEfficiencyCorrectionFactor(sqe, n_e=10, n_lam=5)

    ee, ll = energy_lambda_nrange(15.0, 6.0, 0.12, 10000, 20)

#    print(detector_efficiency(ee, ll, 1) * decf(ee, ll))
    print(trapz(trapz(decf(ee, ll) * decf.legacy_calc(ee, ll, 0), ee, axis=0), ll[0]))
#    print(trapz(trapz(ones(ll.shape), ee, axis=0), ll[0]))
    print(trapz(trapz(decf.legacy_calc(ee, ll, 1), ee, axis=0), ll[0]))
    print(trapz(trapz(decf.legacy_calc(ee, ll, 0), ee, axis=0), ll[0]))
    print(trapz(trapz(decf.legacy_calc(ee, ll, 0), ee, axis=0)/trapz(trapz(decf.legacy_calc(ee, ll, 1), ee, axis=0), ll[0]), ll[0]))
#    print(detector_efficiency(ee[::500, ::5], ll[::500, ::5], 0))
#    print()



#------------------------------------------------------------------------------

if __name__ == "__main__":
#    test_CorrectionFactor_instantiation()
#    test_DetectorEfficiencyCorrectionFactor()
#    test_EnergyCutOffCorrectionFactor()
#    test_correctionFactor_dimensionality()
#    test_EnergyCutoffCorrectionFactor()
    test_DetectorEfficiency_cancel()