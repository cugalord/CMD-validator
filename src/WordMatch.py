# uses levenshtein distance to compare two words and return the most similar word
# the similarity score is calculated as 1 - (levenshtein_distance / max_len)
# is not case sensitive
class WordMatch:
    def __init__(self):
        pass

    # https://en.wikipedia.org/wiki/Levenshtein_distance
    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        # len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def similarity_score(self   , s1, s2):
        lev_distance = self.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        return 1 - lev_distance / max_len

    # comare the source word with the solution words and return the most similar word score
    def compare_word(self, src_w: str, sol_words: list[str]) -> list[str | float]:
        results_table = []
        for sol_word in sol_words:
            score = self.similarity_score(src_w.upper(), sol_word.upper())
            results_table.append([sol_word, score])

        if len(results_table) == 0:
            return [src_w, 0.0]
        return sorted(results_table, key=lambda x: x[1], reverse=True)[0]


if __name__ == '__main__':
    wm = WordMatch()
    #print(wm.compare_word("rojstvo", ['rojstvo', 'datum_rojstva']))
    #print(wm.compare_word("datumRoj", ['Student', 'datum_rojstva']))
    print((wm.compare_word("telefonska številka", ['tel. številka'])))

