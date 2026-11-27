extern "C" unsigned hcr2_fixture(unsigned lhs, unsigned rhs) {
    return (lhs ^ (rhs + 18u)) * 33u;
}
