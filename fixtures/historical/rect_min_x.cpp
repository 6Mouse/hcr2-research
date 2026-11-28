struct Origin {
    float x;
    float y;
};

extern "C" float min_x(const Origin& origin) {
    // Inferred: this models the historical accessor's first-field read as an origin coordinate.
    // Unknown: the corresponding 1.76.1 layout and symbol identity.
    return origin.x;
}

extern "C" float negative_control(const Origin& origin) {
    return origin.y;
}
