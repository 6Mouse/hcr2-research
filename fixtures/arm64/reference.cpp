extern "C" unsigned hcr2_fixture(unsigned lhs, unsigned rhs) {
    return (lhs ^ (rhs + 17u)) * 33u;
}
