# Environment variables

ifeq ($(origin FFLAGS),undefined)
  #FFLAGS= -O -w
  FFLAGS = -O -fno-automatic
  #FFLAGS+= -g -fbounds-check -ffpe-trap=invalid,zero,overflow,underflow,denormal -Wall
endif

ifeq ($(origin CXXFLAGS),undefined)
  #CXXFLAGS= -g 
  CXXFLAGS = -O 
endif

ifeq ($(origin CFLAGS),undefined)
  #CFLAGS= -g 
  CFLAGS = -O 
endif

  

FFLAGS+= -ffixed-line-length-132

# Set FC unless it's defined by an environment variable
ifeq ($(origin FC),default)
#  FC=g77
#  FC=gfortran
   FC=/afs/cern.ch/sw/lcg/external/gcc/4.7.0/x86_64-slc5-gcc47-opt/bin/gfortran
endif

FC = /usr/local/bin/gfortran

# Options: dynamic, lhapdf

UNAME := $(shell uname)

# Option dynamic

ifdef dynamic
  ifeq ($(UNAME), Darwin)
    libext=dylib
    FFLAGS+= -fno-common
    LDFLAGS += -bundle
    define CREATELIB
      $(FC) -dynamiclib -undefined dynamic_lookup -o $(1) $(2)
    endef
  else
    libext=so
    FFLAGS+= -fPIC
    LDFLAGS += -shared
    define CREATELIB
      $(FC) $(FFLAGS) $(LDFLAGS) -o $(1) $(2)
    endef
  endif
else
  libext=a
  define CREATELIB
    $(AR) cru $(1) $(2)
    ranlib $(1)
  endef
endif

# Option lhapdf

ifdef lhapdf
  alfas_functions=alfas_functions_lhapdf
  lhapdf=-lLHAPDF -lstdc++
  reweight_xsec_events_pdf_dummy=
else
  alfas_functions=alfas_functions
  lhapdf=
  reweight_xsec_events_pdf_dummy=reweight_xsec_events_pdf_dummy.o
endif

# Madloop
ifdef madloop
  %(pjdir)s
  libmadloop=libMadLoop.a
  libcuttools=-lcts %(link_tir_libs)s
else
  libmadloop=
  libcuttools=
endif

# OLP (virtuals) necessary link
libOLP=