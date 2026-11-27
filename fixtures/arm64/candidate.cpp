extern "C" unsigned hcr2_fixture(unsigned lhs, unsigned rhs) {
    const unsigned mixed = lhs ^ (rhs + 17u);
    return mixed + (mixed << 5);
}
