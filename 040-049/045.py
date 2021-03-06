from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class Morph:
    surface: str
    base: str
    pos: str
    pos1: str


@dataclass
class Chunk:
    dst: str # 係り先
    srcs: List[str] # 係り元
    morphs: List[Morph]

    @property
    def norm_surface(self) -> str:
        return ''.join(map(lambda x: x.surface, filter(lambda x: x.pos != '記号', self.morphs)))


class Loader:
    def __init__(self, filename: str):
        self._filename = filename

    def __iter__(self) -> List[Morph]:
        with open(self._filename, 'rt') as f:
            chunks = []
            chunk = None
            for line in f:
                sentence = line.strip()
                if sentence[0] == '*':
                    if chunk is not None:
                        chunks.append(chunk)
                    items = sentence.split()
                    chunk = Chunk(dst=items[1], srcs=[items[2].replace('D', '')], morphs=[])
                elif sentence == 'EOS':
                    if chunk is not None:
                        chunks.append(chunk)
                    yield chunks
                    chunks = []
                else:
                    items = sentence.split('\t')
                    results = items[1].split(',')
                    morph = Morph(
                        surface=items[0],
                        base=results[6],
                        pos=results[0],
                        pos1=results[1]
                    )
                    if morph.pos in ['動詞', '助詞']:
                        # print(morph.pos, morph.base)
                        chunk.morphs.append(morph)


def find_verb(chunks: List[Chunk]) -> Tuple[int, Morph]:
    for i, chunk in enumerate(chunks):
        for morph in chunk.morphs:
            if morph.pos == '動詞':
                return i, morph
    return -1, None


def find_cases(chunks: List[Chunk], index: int) -> List[Morph]:
    morphs = []
    s_index = str(index)
    for chunk in chunks:
        if s_index in chunk.srcs:
            morphs.extend(chunk.morphs)
    return morphs


def main():
    # loader = Loader('ai.ja.txt.parsed')
    loader = Loader('sample.txt.parsed')
    sentence_chunks = []
    for sentence_chunk in loader:
        if sentence_chunk == []:
            continue
        sentence_chunks.append(sentence_chunk)

    # print(sentence_chunks)
    # print()
    for chunks in sentence_chunks:
        index, morph = find_verb(chunks)
        if index == -1:
            continue
        cases = find_cases(chunks, index)
        result = [morph.base] + [case.base for case in cases]
        print(' '.join(result))


    print('DONE')


if __name__ == '__main__':
    main()
