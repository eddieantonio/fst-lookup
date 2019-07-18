import time

from fst_lookup import FST


def test_hfstol_analysis_performance(cree_hfstol_analyzer: FST, cree_foma_analyzer: FST):
    """
    Test hfstol analysis has at least 100 times the performance when there are 800 words
    """
    data = ["niskak"]*800
    time0 = time.time()
    for _ in list(cree_hfstol_analyzer.analyze_in_bulk(data)):
        list(_)

    time1 = time.time()

    time2 = time.time()
    for _ in list(cree_foma_analyzer.analyze_in_bulk(data)):
        list(_)
    time3 = time.time()

    a = 100*(time1-time0)
    b = time3-time2
    print(a, b)
    assert a < b

def test_hfstol_generation_performance(cree_hfstol_generator: FST, cree_foma_generator: FST):
    """
    Test hfstol generation has at least 100 times the performance when there are 150 words
    """
    data = [''.join(('nîskâw', '+V', '+II', '+Cnj', '+Prs', '+3Sg'))]*150
    time0 = time.time()
    for _ in list(cree_hfstol_generator.generate_in_bulk(data)):
        list(_)

    time1 = time.time()

    time2 = time.time()
    for _ in list(cree_foma_generator.generate_in_bulk(data)):
        list(_)
    time3 = time.time()

    a = 100*(time1-time0)
    b = time3-time2
    print(a, b)
    assert a < b