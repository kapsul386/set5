#include <bits/stdc++.h>
using namespace std;

struct HyperMegaLogLogProMax {
    static const int B = 14;
    static const int Q = 1 << B;
    static const int L = 32;

    unsigned char reg[Q];
    double invPow2[64];

    HyperMegaLogLogProMax() {
        for (int i = 0; i < Q; i++) reg[i] = 0;

        for (int r = 0; r < 64; r++) invPow2[r] = pow(2.0, -r);
    }

    unsigned int hash32(const string &s) {
        uint32_t h = 2166136261u;
        uint32_t p = 16777619u;
        for (int i = 0; i < (int)s.size(); i++) {
            h ^= (uint32_t)(unsigned char)s[i];
            h *= p;
        }
        return h;
    }

    double alpha_q(int q) {
        if (q == 2) return 0.3512;
        if (q == 4) return 0.5324;
        if (q == 16) return 0.673;
        if (q == 32) return 0.697;
        if (q == 64) return 0.709;
        return 0.7213 / (1.0 + 1.079 / q);
    }

    int rho_tail(unsigned int h) {
        int rem = L - B;
        unsigned int mask = (1u << rem) - 1u;
        unsigned int tail = h & mask;

        if (tail == 0) return rem + 1;

        int r = 1;
        for (int k = rem - 1; k >= 0; k--) {
            if ((tail >> k) & 1u) break;
            r++;
        }
        return r;
    }

    void add(const string &x) {
        unsigned int h = hash32(x);

        int idx = (int)(h >> (L - B));

        int r = rho_tail(h);

        if ((int)reg[idx] < r) reg[idx] = (unsigned char)r;
    }

    double estimate() {
        double a = alpha_q(Q);

        double sum = 0.0;
        int zeros = 0;

        for (int i = 0; i < Q; i++) {
            int r = (int)reg[i];
            sum += invPow2[r];
            if (r == 0) zeros++;
        }

        double E = a * (double)Q * (double)Q / sum;

        if (E <= 2.5 * Q && zeros > 0) {
            E = (double)Q * log((double)Q / zeros);
        }

        return E;
    }

    double estimate_stream(const vector<string> &stream) {
        for (int i = 0; i < (int)stream.size(); i++) add(stream[i]);
        return estimate();
    }

    void reset() {
        for (int i = 0; i < Q; i++) reg[i] = 0;
    }
};
