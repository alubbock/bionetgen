# BioNetGen

Rule-based modeling framework
[![Build Status](https://travis-ci.org/RuleWorld/bionetgen.svg?branch=master)](https://travis-ci.org/RuleWorld/bionetgen)
[![Build status](https://ci.appveyor.com/api/projects/status/f7klreiao20ylwon?svg=true)](https://ci.appveyor.com/project/jczech/bionetgen)

## Overview

BioNetGen is software for the specification and simulation of rule-based models
of biochemical systems, including signal transduction, metabolic, and genetic
regulatory networks. The BioNetGen language has recently been extended to
include explicit representation of compartments. A recent review of methods for
rule-based modeling is available in L. A. Chylek et al. (2013) Wiley
Interdiscip. Rev. Syst. Biol. Med., 6, 13–36.

BioNetGen is presently a mixture of Perl, C++, and Python. Network generation
is currently implemented in Perl, the network simulator is C++, and a new
SBML-to-BNGL translator is implemented in Python. In addition, a new language
parser is currently being developed in ANTLR.

## Installation of Distribution 

Most users should simply download BioNetGen from www.bionetgen.org and get the
appropriate distribution for their OS. To install BioNetGen, unzip the
BioNetGen distribution file, e.g.  BioNetGen-2.3-MacOSX.tar.gz, in the
directory where you would like BioNetGen installed. 

## Download Latest Test Builds

These builds are the from the head of master and are not guaranteed to be
stable. Use at your own risk.

* [Linux](https://bintray.com/jczech/bionetgen/download_file?file_path=BioNetGen-2.3.2-linux.tar.gz)
* [OSX](https://bintray.com/jczech/bionetgen/download_file?file_path=BioNetGen-2.3.2-osx.tar.gz)
* [Windows x64](https://bintray.com/jczech/bionetgen/download_file?file_path=BioNetGen-2.3.2-Win-x64.zip)

## Compilation from Source

The distribution mentioned above comes with pre-compiled binaries (executables)
for the ODE, SSA and PLA engines. However, developers can compile their own
binaries assuming they have appropriate compilation tools (autoconf, etc).

First, you'll need to pull in or update the git submodules (currently NFsim and
atomizer). To do this, enter the following at the terminal:

    git submodule init
    git submodule update

### Linux and OSX

At a terminal, type the following to build NFsim and atomizer:

    cd <bngpath>
    make
	
### Windows

#### NFsim and atomizer

Make sure you have Ninja, CMake, and Anaconda installed and that Python is in
your path. For more detailed information, please see the NFsim and atomizer
repos. From a PowerShell prompt, type the following:

    cd <bngpath>/atomizer/SBMLparser
    python.exe -m pip install --user -r ./requirements_win.txt
    python.exe -m pip install --target=. python-libsbml
    python.exe -m PyInstaller ./sbmlTranslator.spec
    mv ./dist/sbmlTranslator.exe ../../bin
    cd ../../nfsim_src
    mkdir build
    cd build
    cmake -G "Ninja" ..
    ninja

#### CVODE and muparser

If you have Windows, try Strawberry Perl, (see http://strawberryperl.com/).
Perl is also available for Windows users within the Cygwin environment.

Make sure Cygwin used is for the appropriate Windows architecture (32/64 bit).
Make sure Cygwin has developer tools installed (Select Devel when installing
Cygwin).  Extract folders `cvode-2.6.0` and `muparser_v2_2_4` to
`<bngpath>\Network3` from archives in `<bngpath>\libsource`. In the Cygwin
terminal:

    cd <bngpath>\Network3
    autoreconf --no-recursive --install
    ./configure --disable-shared --prefix=<bngpath>
    make
    make install
    make clean

Using BioNetGen from the Windows command prompt can throw Missing DLL errors.
These DLLs are specific to the Cygwin version used and found in Cygwin\bin.
Copy them to `<bngpath>\bin` to resolve these errors. The required DLLs for the
64-bit version are:

* cygwin1.dll
* cygstdc++-6.dll
* cygz.dll
* cyggcc_s-seh-1.dll.

## Creating a Distribution

Developers preparing a new distribution can simply run the following command:

    cd <bngpath>
    make dist

This will create a tarball called '<bngpath>/BioNetGen-<version>.tgz'.

## Examples

Example models are provided in the Models2 folder. To run them, go to the
Models2 directory, and type:

    ../BNG2.pl <model>.bngl

where <model> is one of the models found in the Models2 directory.

## Validation

To validate the BioNetGen installation:
1) run the Perl script `<bngpath>/Validate/validate_examples.pl`.
2) if any tests fail, look at the log files for more information.

PLEASE NOTE: Stochastic simulation tests rely on statistical validation.
Occasionally a validation will fail due to outliers. The current validation
script only reports stochastic validation failures if they occur TWICE in
a row. Therefore, if this occurs there is a good chance that something is
wrong. To confirm, we suggest rerunning the validation script at least once.
Single tests may be run by passing the model basename as an argument.

## BioNetGen History and Support

The BioNetGen software package was initially developed by the Cell Signaling
Team at Los Alamos National Laboratory. The current development team is based
in the Department of Computational and Systems Biology at the University of
Pittsburgh School of Medicine, with contributions from collaborators at the
Theoretical Division and Center for Nonlinear Studies at Los Alamos National
Laboratory, the Departments of Biology and Computer Science at the University
of New Mexico, the Center for Cell Analysis and Modeling at the University of
Connecticut Health Center, and the Department of Biological Chemistry at the
Johns Hopkins University School of Medicine.

BioNetGen development is currently supported under the auspices of the Center
for Multiscale Modeling of Biological Systems (MMBioS), a collaboration between
the University of Pittsburgh, the Pittsburgh Supercomputing Center, Carnegie
Mellon University, and the Salk Institute (NIH grant P41GM103712). BioNetGen
has been supported by NIH grant GM076570 and work has been performed under DOE
contract DE-AC52-06NA25396. Additional support for BioNetGen has been provided
by NIH grants GM085273, AI35997, and CA109552, NSF grant 0829788, the Arizona
Biomedical Research Commission, and the Department of Computational Biology at
the University of Pittsburgh School of Medicine.

## Distributions

The latest BioNetGen distributions, release notes, installation guides, 
tutorials, etc. are available at http://bionetgen.org.

RuleBender, a Java-based graphical front end for BioNetGen, is available at
http://rulebender.org. RuleBender is supported on Linux, Mac OS/X, and Windows
platforms. A compatible version of BioNetGen is included in the RuleBender
distribution. If you are not sure if your version of BNG is compatible with
RuleBender, please use the version distributed with RuleBender.

## Contact Us

Email the developers at bionetgen.help@gmail.com

## Troubleshooting

If you see the message `ABORT: Could not find executable run_network`, try
setting the environment variable "BNGPATH" to the root directory of your 
BioNetGen installation. Under bash-like shells, this is done by typing:
`export BNGPATH=<bngpath>`, where <bngpath> is the root directory of BNG.
