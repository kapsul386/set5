#include <bits/stdc++.h>
using namespace std;

const int N = 10000;
const int RUNS = 50;
const int STEPS = 20;

// FAST может иметь B до 16 (q=65536)
const int MAX_Q = 1 << 16;

double invPow2[64];

/* -------- FNV-1a 32-bit -------- */
unsigned int hash32(const string &s) {
    uint32_t h = 2166136261u;
    uint32_t p = 16777619u;
    for (int i = 0; i < (int)s.size(); i++) {
        h ^= (uint32_t)(unsigned char)s[i];
        h *= p;
    }
    return (unsigned int)h;
}

/* -------- Random stream -------- */
string random_string() {
    static string alphabet =
        "qwertyuiopasdfghjklzxcvbnm"
        "QWERTYUIOPASDFGHJKLZXCVBNM"
        "0123456789-";

    int len = 1 + (rand() % 30);
    string s;
    s.reserve(len);
    for (int i = 0; i < len; i++) {
        int id = rand() % (int)alphabet.size();
        s.push_back(alphabet[id]);
    }
    return s;
}

/*
  -------- rho(w) по определению HLL --------
  Берём хвост из (32 - B) бит:
  tail = h & ((1<<(32-B)) - 1)

  rho(tail) = (число ведущих нулей в этих rem битах) + 1
  если tail == 0 => rho = rem + 1
*/
int rho_tail(unsigned int h, int B) {
    int rem = 32 - B;

    // если rem == 32 (B==0), маска (1<<32) невалидна, но у нас B>=4 всегда
    unsigned int mask = (1u << rem) - 1u;
    unsigned int tail = h & mask;     // ровно rem младших бит

    if (tail == 0) return rem + 1;

    int r = 1;
    // ищем первую 1, начиная со старшего бита tail (k = rem-1)
    for (int k = rem - 1; k >= 0; k--) {
        if ((tail >> k) & 1u) break;
        r++;
    }
    return r;
}

/* -------- alpha -------- */
double alpha_q(int q) {
    if (q == 2) return 0.3512;
    if (q == 4) return 0.5324;
    if (q == 16) return 0.673;
    if (q == 32) return 0.697;
    if (q == 64) return 0.709;
    return 0.7213 / (1.0 + 1.079 / q);
}

double hll(int rank_arr[], int q) {
    double a = alpha_q(q);

    double sum = 0.0;
    int zeros = 0;

    for (int j = 0; j < q; j++) {
        sum += pow(2.0, -rank_arr[j]);
        if (rank_arr[j] == 0) zeros++;
    }

    double E = a * (double)q * (double)q / sum;

    if (E <= 2.5 * q && zeros > 0) {
        E = (double)q * log((double)q / zeros);
    }
    return E;
}

double hll_optimized(unsigned char rank_arr[], int q) {
    double a = alpha_q(q);

    double sum = 0.0;
    int zeros = 0;

    for (int j = 0; j < q; j++) {
        int r = (int)rank_arr[j];
        sum += invPow2[r];
        if (r == 0) zeros++;
    }

    double E = a * (double)q * (double)q / sum;

    if (E <= 2.5 * q && zeros > 0) {
        E = (double)q * log((double)q / zeros);
    }
    return E;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    srand((unsigned)time(0));

    for (int i = 0; i < 64; i++) invPow2[i] = pow(2.0, -i);

    int B_values_slow[] = {4, 6, 8, 10, 12};
    int B_cnt_slow = 5;

    int B_values_fast[] = {4, 6, 8, 10, 12, 14, 16};
    int B_cnt_fast = 7;

    ofstream fout("results.csv");
    fout << "mode,B,run,t,F0_true,F0_est\n";

    for (int run = 0; run < RUNS; run++) {
        vector<string> stream(N);
        for (int i = 0; i < N; i++) {
            if (i > 0 && (rand() % 5 == 0)) stream[i] = stream[rand() % i];
            else stream[i] = random_string();
        }

        for (int bi = 0; bi < B_cnt_slow; bi++) {
            int B = B_values_slow[bi];
            int q = 1 << B;

            static int rank_slow[MAX_Q];
            for (int j = 0; j < q; j++) rank_slow[j] = 0;

            unordered_set<string> exact;
            exact.reserve(N * 2);

            for (int i = 0; i < N; i++) {
                exact.insert(stream[i]);

                unsigned int h = hash32(stream[i]);

                int idx = (int)(h >> (32 - B));

                int r = rho_tail(h, B);

                if (rank_slow[idx] < r) rank_slow[idx] = r;

                if ((i + 1) % (N / STEPS) == 0) {
                    double est = hll(rank_slow, q);
                    fout << "slow," << B << "," << run << "," << (i + 1) << ","
                         << (int)exact.size() << "," << est << "\n";
                }
            }
        }

        for (int bi = 0; bi < B_cnt_fast; bi++) {
            int B = B_values_fast[bi];
            int q = 1 << B;

            static unsigned char rank_fast[MAX_Q];
            for (int j = 0; j < q; j++) rank_fast[j] = 0;

            unordered_set<string> exact;
            exact.reserve(N * 2);

            for (int i = 0; i < N; i++) {
                exact.insert(stream[i]);

                unsigned int h = hash32(stream[i]);

                int idx = (int)(h >> (32 - B));
                int r = rho_tail(h, B);

                if ((int)rank_fast[idx] < r) rank_fast[idx] = (unsigned char)r;

                if ((i + 1) % (N / STEPS) == 0) {
                    double est = hll_optimized(rank_fast, q);
                    fout << "fast," << B << "," << run << "," << (i + 1) << ","
                         << (int)exact.size() << "," << est << "\n";
                }
            }
        }
    }

    fout.close();
    return 0;
}
