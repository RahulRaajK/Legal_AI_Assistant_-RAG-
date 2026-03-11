"""Seed data: Landmark Supreme Court cases."""
from backend.ingestion.pipeline import ingestion_pipeline


def seed_landmark_cases():
    """Seed landmark Supreme Court and High Court judgments."""
    cases = [
        {
            "title": "Kesavananda Bharati v. State of Kerala (1973)",
            "content": """Kesavananda Bharati v. State of Kerala (1973) 4 SCC 225 — This is the most important constitutional law case in India. A 13-judge bench of the Supreme Court held that Parliament has wide powers to amend the Constitution under Article 368, but it cannot alter the 'basic structure' of the Constitution. The basic structure doctrine includes: supremacy of the Constitution, republican and democratic form of government, secular character of the Constitution, separation of powers between legislature, executive and judiciary, federal character of the Constitution, unity and sovereignty of India, individual freedom, the mandate to build a welfare state, rule of law, judicial review, and free and fair elections. This case overruled the earlier decision in Golak Nath v. State of Punjab (1967). Chief Justice Sikri delivered the majority opinion.""",
            "court": "Supreme Court of India",
            "judge": "Chief Justice S.M. Sikri",
            "year": 1973,
            "citation": "(1973) 4 SCC 225",
            "cited_sections": ["constitution_of_india_s368"],
        },
        {
            "title": "Maneka Gandhi v. Union of India (1978)",
            "content": """Maneka Gandhi v. Union of India AIR 1978 SC 597 — The Supreme Court expanded the scope of Article 21 (Right to Life and Personal Liberty). The Court held that the right to 'life' in Article 21 means the right to live with human dignity and not merely animal existence. The procedure established by law under Article 21 must be right, just, and fair, and not arbitrary, fanciful, or oppressive. This case also established that Articles 14, 19, and 21 are not watertight compartments but are interconnected — a law depriving personal liberty must also satisfy the requirements of Articles 14 and 19. Justice P.N. Bhagwati delivered the majority opinion. This case is the foundation for the expansive interpretation of fundamental rights in India and overruled the narrow interpretation in A.K. Gopalan v. State of Madras (1950).""",
            "court": "Supreme Court of India",
            "judge": "Justice P.N. Bhagwati",
            "year": 1978,
            "citation": "AIR 1978 SC 597",
            "cited_sections": ["constitution_of_india_s21", "constitution_of_india_s14", "constitution_of_india_s19"],
        },
        {
            "title": "Vishaka v. State of Rajasthan (1997)",
            "content": """Vishaka v. State of Rajasthan AIR 1997 SC 3011 — The Supreme Court laid down guidelines to address sexual harassment at the workplace. In the absence of specific legislation, the Court formulated the 'Vishaka Guidelines' which were binding on all employers. These guidelines defined sexual harassment, placed obligations on employers to prevent it, and established a complaints committee mechanism. This case led to the enactment of the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013. Chief Justice J.S. Verma authored the judgment. The Court relied on Articles 14, 15, 19(1)(g), and 21 of the Constitution and CEDAW (Convention on the Elimination of All Forms of Discrimination Against Women).""",
            "court": "Supreme Court of India",
            "judge": "Chief Justice J.S. Verma",
            "year": 1997,
            "citation": "AIR 1997 SC 3011",
            "cited_sections": ["constitution_of_india_s14", "constitution_of_india_s21"],
        },
        {
            "title": "K.S. Puttaswamy v. Union of India (2017)",
            "content": """Justice K.S. Puttaswamy (Retd.) v. Union of India (2017) 10 SCC 1 — A nine-judge bench of the Supreme Court unanimously held that the right to privacy is a fundamental right protected under Articles 14, 19, and 21 of the Constitution. Justice D.Y. Chandrachud wrote the lead opinion. The Court held that privacy includes informational privacy, privacy of choice, and bodily integrity. The right to privacy is not absolute and can be restricted by procedure established by law if it satisfies the three-fold requirement: (1) legality (existence of law), (2) legitimate aim (need defined in terms of a legitimate state interest), and (3) proportionality (proportional to the need). This case overruled the earlier 8-judge bench decision in M.P. Sharma v. Satish Chandra (1954) and 6-judge bench decision in Kharak Singh v. State of U.P. (1963) to the extent they held that privacy is not a fundamental right.""",
            "court": "Supreme Court of India",
            "judge": "Justice D.Y. Chandrachud",
            "year": 2017,
            "citation": "(2017) 10 SCC 1",
            "cited_sections": ["constitution_of_india_s21", "constitution_of_india_s14", "constitution_of_india_s19"],
        },
        {
            "title": "Navtej Singh Johar v. Union of India (2018)",
            "content": """Navtej Singh Johar v. Union of India (2018) 10 SCC 1 — A five-judge Constitution bench of the Supreme Court decriminalized consensual same-sex relations by reading down Section 377 of the IPC. The Court held that Section 377 was unconstitutional insofar as it criminalizes consensual sexual conduct between adults of the same sex. Chief Justice Dipak Misra and Justices R.F. Nariman, A.M. Khanwilkar, D.Y. Chandrachud, and Indu Malhotra delivered separate concurring opinions. The Court held that sexual orientation is an integral part of the identity of an individual and is protected under Articles 14, 15, 19, and 21.""",
            "court": "Supreme Court of India",
            "judge": "Chief Justice Dipak Misra",
            "year": 2018,
            "citation": "(2018) 10 SCC 1",
            "cited_sections": ["constitution_of_india_s14", "constitution_of_india_s21"],
        },
        {
            "title": "Arnesh Kumar v. State of Bihar (2014)",
            "content": """Arnesh Kumar v. State of Bihar (2014) 8 SCC 273 — The Supreme Court laid down guidelines to prevent automatic arrests under Section 498A IPC (cruelty by husband) and dowry prohibition cases. The Court held that police officers must satisfy themselves about the necessity for arrest under Section 41 CrPC before making an arrest. Magistrates must be satisfied that the conditions for arrest were met before authorising detention. Non-compliance may lead to departmental action against the police officer and contempt of court proceedings against the magistrate. Justice C.K. Prasad delivered the judgment.""",
            "court": "Supreme Court of India",
            "judge": "Justice C.K. Prasad",
            "year": 2014,
            "citation": "(2014) 8 SCC 273",
            "cited_sections": ["indian_penal_code_s498A"],
        },
        {
            "title": "Bachan Singh v. State of Punjab (1980)",
            "content": """Bachan Singh v. State of Punjab (1980) 2 SCC 684 — The Supreme Court upheld the constitutional validity of the death penalty under Section 302 IPC. However, the Court established the 'rarest of rare' doctrine, holding that the death sentence should be imposed only in the 'rarest of rare cases' when the alternative option of life imprisonment is unquestionably foreclosed. The Court laid down aggravating and mitigating circumstances to guide judges in deciding whether to impose the death penalty. Justice Sarkaria delivered the majority opinion. Justice P.N. Bhagwati dissented, arguing that the death penalty violates Articles 14 and 21.""",
            "court": "Supreme Court of India",
            "judge": "Justice P.N. Bhagwati (dissent), Justice Sarkaria (majority)",
            "year": 1980,
            "citation": "(1980) 2 SCC 684",
            "cited_sections": ["indian_penal_code_s302", "constitution_of_india_s21"],
        },
        {
            "title": "M.C. Mehta v. Union of India (1987) - Oleum Gas Leak Case",
            "content": """M.C. Mehta v. Union of India AIR 1987 SC 1086 — The Supreme Court established the principle of 'absolute liability' for industries engaged in hazardous or inherently dangerous activities. This went beyond the strict liability principle from Rylands v. Fletcher. The Court held that an enterprise engaged in a hazardous or inherently dangerous industry owes an absolute and non-delegable duty to the community to ensure no harm occurs. If harm results, the enterprise must compensate all affected persons regardless of whether it exercised due diligence. This case arose from the Oleum gas leak from Shriram Food & Fertilizer Complex in Delhi. Justice P.N. Bhagwati delivered the judgment. The principle established is also relevant to environmental law and the right to clean environment under Article 21.""",
            "court": "Supreme Court of India",
            "judge": "Justice P.N. Bhagwati",
            "year": 1987,
            "citation": "AIR 1987 SC 1086",
            "cited_sections": ["constitution_of_india_s21"],
        },
    ]
    
    print("⚖️ Seeding Landmark Cases...")
    results = []
    for case in cases:
        result = ingestion_pipeline.ingest_case(**case)
        print(f"  ✅ {case['title']}")
        results.append(result)
    
    print(f"✅ All {len(cases)} landmark cases seeded!")
    return results


if __name__ == "__main__":
    seed_landmark_cases()
