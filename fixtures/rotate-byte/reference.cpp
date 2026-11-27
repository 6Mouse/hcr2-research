extern "C" unsigned rotate_byte(unsigned value) {
    return ((value << 3) | (value >> 5)) & 255u;
}
