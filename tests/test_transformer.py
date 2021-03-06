import matplotlib.pyplot as plt
###############################################################################
from numpy import linspace, logspace, tile, trapz, all, isclose, abs
###############################################################################
from modelmiezelb.correction import CorrectionFactor, DetectorEfficiencyCorrectionFactor, EnergyCutOffCorrectionFactor
from modelmiezelb.lineshape import LorentzianLine
from modelmiezelb.sqe_model import SqE, SqE_from_arg
from modelmiezelb.transformer import SqtTransformer
###############################################################################
from modelmiezelb.utils.util import MIEZE_DeltaFreq_from_time, energy_from_lambda, MIEZE_phase, detector_efficiency, triangle_distribution
###############################################################################
import modelmiezelb.arg_inel_mieze_model as arg

def test_transformer_init():
    ### Creating a SqE model for transformation
    # We need some lines
    L1 = LorentzianLine("Lorentzian1", (-5.0, 5.0), x0=0.0, width=0.4, c=0.0, weight=2)
    L2 = LorentzianLine(name="Lorentzian2", domain=(-5.0, 5.0), x0=-1.0, width=0.4, c=0.0, weight=1)
    # Contruct a SqE model
    sqe1 = SqE(lines=(L2,), lam=6.0, dlam=0.12, l_SD=3.43, T=20)
    SqE(lines=(L1, L2), lam=6.0, dlam=0.12, l_SD=3.43, T=20)

    ### Instantiate a transformer
    SqtTransformer(sqe1, n_lam=20, n_e=10000)

#------------------------------------------------------------------------------

def test_transformer_basics():
    ### Creating a SqE model for transformation
    # We need some lines
    L1 = LorentzianLine(name="Lorentzian1", domain=(-15.0, 15.0), x0=-1.0, width=0.4, c=0.0, weight=3)
    # Contruct a SqE model
    sqe1 = SqE(lines=(L1,), lam=6.0, dlam=0.12, l_SD=3.43, T=20)

    ### Instantiate a transformer
    sqt1 = SqtTransformer(
        sqe1,
        corrections=(DetectorEfficiencyCorrectionFactor(sqe1, n_e=15000, n_lam=20),),
        n_e=15000,
        n_lam=20,
        l_SD=3.43
    )

    ### Values for transformation
    taus = logspace(-6, -1, 11)
    freqs = MIEZE_DeltaFreq_from_time(taus*1.0e-9, 3.43, 6.0)

    ### TRANSFORM!!
    sqt1vals = [sqt1(freq) for freq in freqs]
    sqt1vals_arg = arg.Sqt(
        arg.fqe_I,
        freqs,
        -1.0,
        0.4,
        15000,
        20,
        3.43,
        6.0,
        0.12,
        0.0,
        1.0,
        20,
        0.00005,
        0.1,
        350.
    )

    ### Visualize results
    # print(sqt1vals)
    # plt.plot(taus, abs(sqt1vals), ls="-", marker="o", label="modelmieze")
    # plt.plot(taus, sqt1vals_arg, ls=":", marker="s", label="arg")
    # plt.xscale("log")
    # plt.legend()
    # plt.show()

#------------------------------------------------------------------------------

def test_transform_arg_model():
    ### Creating a SqE model for transformation
    sqe_arg = SqE_from_arg(T=20.)

    ### Instantiate a transformer
    sqt_arg = SqtTransformer(
        sqe_arg,
        corrections=(DetectorEfficiencyCorrectionFactor(sqe_arg, n_e=15000, n_lam=20),),
        n_e=15000,
        n_lam=20,
        l_SD=3.43
    )

    ### Values for transformation
    taus = logspace(-6, -1, 11)
    freqs = MIEZE_DeltaFreq_from_time(taus*1.0e-9, 3.43, 6.0)

    ### TRANSFORM!!
    sqt_argvals = [sqt_arg(freq) for freq in freqs]
    # For the next step to work, A1 needs to be manually removed
    # from arg.Sqt calculation.
    sqt_argmodulevals = arg.Sqt(
        arg.fqe_I,
        freqs,
        -1.0,
        0.4,
        15000,
        20,
        3.43,
        6.0,
        0.12,
        0.0,
        1.0,
        20,
        0.00005,
        0.1,
        350.
    )

    # plt.plot(taus, sqt_argvals, label="arg-model")
    # plt.plot(taus, sqt_argmodulevals, label="arg-model from mod")
    # plt.legend()
    # plt.xscale("log")
    # plt.show()

#------------------------------------------------------------------------------

def test_manualtransform_arg_model():
    ### Creating a SqE model for transformation
    sqe_arg = SqE_from_arg(T=20.)
    ### Creating energy, wavelength parameter space
    lam = sqe_arg.model_params["lam"]
    dlam = sqe_arg.model_params["dlam"]
    n_lam = 5   #20
    n_e = 10    #15000
    l_SD = 3.43

    l = linspace(1-dlam*1.01, 1+dlam*1.01, n_lam) * lam
    ll = tile(l,(n_e,1))
    a = -0.99999 * energy_from_lambda(l)
    ee = linspace(a, 15.0, n_e)

    ### Values for transformation
    taus = logspace(-6, -1, 101)
    freqs = MIEZE_DeltaFreq_from_time(taus*1.0e-9, 3.43, 6.0)

    mieze_phase = MIEZE_phase(ee, freqs[30], l_SD, ll)
    det_eff = detector_efficiency(ee, ll, 1)
    tri_distr = triangle_distribution(ll, lam, dlam)

    print(ll)
    print(ee)
    print(mieze_phase)
    print(det_eff)
    print(tri_distr)
    

if __name__ == "__main__":
#    test_transformer_init()
#    test_transformer_basics()
    test_transform_arg_model()
#    test_manualtransform_arg_model()