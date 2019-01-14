#include <stdio.h>
#include <time.h>
#include <math.h>
#include "pcg_basic.h"

/* generates a uniformly random number on the interval (min, max) */ 

static int initflag=1;
    
double RANDOM( double min, double max){
    /* seed random number generator from the current time */
    if (initflag){
        // Seed with external entropy -- the time and some program addresses
        // (which will actually be somewhat random on most modern systems).
        // A better solution, entropy_getbytes, using /dev/random, is provided
        // in the full pcg library.

        pcg32_srandom(time(NULL) ^ (intptr_t)&printf, time(NULL) ^ (intptr_t)&printf);
	initflag=0;
    }

    // This only generates numbers rounded to the nearest multiple of 1/2**32, which
    // matches the original implementation.
    // http://www.pcg-random.org/using-pcg-c-basic.html#pcg32-boundedrand-r-rngptr-bound
    return( (max-min)*ldexp(pcg32_random(), -32) + min);
}

void SEED_RANDOM( int seed){
    // pcg32_srandom_r takes two 64-bit constants (the initial state, and the
    // rng sequence selector; rngs with different sequence selectors will
    // *never* have random sequences that coincide, at all) - the code below
    // shows three possible ways to do so.

    // for compatibility reasons, we're only supplied one seed
    pcg32_srandom(seed, seed);
    initflag = 0;
}
