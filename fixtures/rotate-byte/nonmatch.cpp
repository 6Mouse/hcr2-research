extern "C" unsigned rotate_byte(unsigned value) {
    return ((value << 2) | (value >> 6)) & 255u;
}
