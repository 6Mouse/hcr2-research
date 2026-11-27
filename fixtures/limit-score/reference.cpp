extern "C" unsigned limit_score(unsigned score, unsigned ceiling) {
    return score < ceiling ? score : ceiling;
}
