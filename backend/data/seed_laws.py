"""Seed data: Major Indian laws pre-packaged for immediate demo."""
from backend.ingestion.pipeline import ingestion_pipeline


def seed_constitution():
    """Seed Constitution of India - Fundamental Rights and key articles."""
    sections = [
        {"number": "14", "title": "Equality before law",
         "text": "Article 14: Equality before law — The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. This article embodies the concept of equality which is a basic feature of the Constitution. It prohibits class legislation but permits reasonable classification. The classification must be founded on an intelligible differentia which distinguishes persons or things grouped together from others, and the differentia must have a rational relation to the object sought to be achieved by the statute. This is one of the most invoked articles in Indian constitutional law."},
        {"number": "19", "title": "Protection of certain rights regarding freedom of speech",
         "text": "Article 19: Protection of certain rights regarding freedom of speech etc. — (1) All citizens shall have the right (a) to freedom of speech and expression; (b) to assemble peaceably and without arms; (c) to form associations or unions; (d) to move freely throughout the territory of India; (e) to reside and settle in any part of the territory of India; (g) to practise any profession, or to carry on any occupation, trade or business. Reasonable restrictions can be imposed under Article 19(2) through (6) in the interests of sovereignty, integrity, security, friendly relations, public order, decency, morality, contempt of court, defamation, or incitement to an offence."},
        {"number": "21", "title": "Protection of life and personal liberty",
         "text": "Article 21: Protection of life and personal liberty — No person shall be deprived of his life or personal liberty except according to procedure established by law. This article has been interpreted expansively by the Supreme Court to include the right to live with dignity, right to livelihood, right to health, right to clean environment, right to privacy (K.S. Puttaswamy v. Union of India 2017), right to education, right to shelter, right to food, right to clean water, right to free legal aid, right to speedy trial, right against solitary confinement, right against delayed execution, right to travel abroad, and many other rights. The procedure established by law must be just, fair, and reasonable (Maneka Gandhi v. Union of India 1978)."},
        {"number": "21A", "title": "Right to education",
         "text": "Article 21A: Right to education — The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine. This article was inserted by the Constitution (Eighty-sixth Amendment) Act, 2002. The Right of Children to Free and Compulsory Education Act, 2009 (RTE Act) was enacted to give effect to this article."},
        {"number": "32", "title": "Remedies for enforcement of rights",
         "text": "Article 32: Remedies for enforcement of rights conferred by this Part — (1) The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed. (2) The Supreme Court shall have power to issue directions or orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari, whichever may be appropriate, for the enforcement of any of the rights conferred by this Part. Dr. B.R. Ambedkar called this article the 'heart and soul of the Constitution'."},
        {"number": "44", "title": "Uniform civil code for the citizens",
         "text": "Article 44: Uniform civil code for the citizens — The State shall endeavour to secure for the citizens a uniform civil code throughout the territory of India. This is a Directive Principle of State Policy. The Supreme Court has on multiple occasions recommended the implementation of a uniform civil code, including in Shah Bano case (1985) and Sarla Mudgal case (1995)."},
        {"number": "226", "title": "Power of High Courts to issue certain writs",
         "text": "Article 226: Power of High Courts to issue certain writs — (1) Every High Court shall have power to issue to any person or authority, including the Government, directions, orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari for the enforcement of any of the rights conferred by Part III and for any other purpose. The jurisdiction under Article 226 is wider than Article 32 as it can be invoked for enforcement of fundamental rights as well as for any other purpose."},
        {"number": "300A", "title": "Persons not to be deprived of property save by authority of law",
         "text": "Article 300A: Persons not to be deprived of property save by authority of law — No person shall be deprived of his property save by authority of law. This article replaced the original fundamental right to property (Article 19(1)(f) and Article 31) which was removed by the 44th Amendment Act, 1978. The right to property is now a constitutional right but not a fundamental right."},
        {"number": "370", "title": "Temporary provisions with respect to Jammu and Kashmir (Abrogated)",
         "text": "Article 370: Temporary provisions with respect to the State of Jammu and Kashmir — This article granted special autonomous status to Jammu and Kashmir. It was effectively abrogated on 5 August 2019 through a Presidential Order (C.O. 272) and confirmed by the Jammu and Kashmir Reorganisation Act, 2019. The Supreme Court in In Re: Article 370 of the Constitution (2023) upheld the abrogation."},
        {"number": "368", "title": "Power of Parliament to amend the Constitution",
         "text": "Article 368: Power of Parliament to amend the Constitution and procedure therefor — (1) Parliament may in exercise of its constituent power amend by way of addition, variation or repeal any provision of this Constitution. The basic structure of the Constitution cannot be amended (Kesavananda Bharati v. State of Kerala 1973). This includes supremacy of the Constitution, republican and democratic form of government, secular character, separation of powers, and federal character."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Constitution of India",
        sections=sections,
        year=1950,
        content_type="statute",
    )
    print(f"✅ Constitution of India seeded: {result}")
    return result


def seed_bns():
    """Seed Bharatiya Nyaya Sanhita 2023 (replaced IPC)."""
    sections = [
        {"number": "1", "title": "Short title, commencement and application",
         "text": "Section 1 of Bharatiya Nyaya Sanhita 2023: Short title, commencement and application — (1) This Sanhita may be called the Bharatiya Nyaya Sanhita, 2023. (2) It shall come into force on the 1st day of July, 2024. (3) Every person shall be liable to punishment under this Sanhita and not otherwise for every act or omission contrary to the provisions thereof, of which he shall be guilty within India."},
        {"number": "63", "title": "Punishment of murder equivalent to IPC 302",
         "text": "Section 63 of Bharatiya Nyaya Sanhita 2023 (equivalent to IPC Section 299/300/302): This section deals with the definition and punishment of culpable homicide and murder. Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine. Murder is defined as culpable homicide with the intention of causing death, or causing such bodily injury as the offender knows to be likely to cause death, or with the intention of causing an injury which is sufficient in the ordinary course of nature to cause death. This replaces sections 299, 300, 302, and 304 of the Indian Penal Code."},
        {"number": "64", "title": "Punishment for culpable homicide not amounting to murder",
         "text": "Section 64 of Bharatiya Nyaya Sanhita 2023 (equivalent to IPC 304): Punishment for culpable homicide not amounting to murder — imprisonment for life or up to ten years and fine. This is a new formulation replacing the IPC's grouping of these offences."},
        {"number": "65", "title": "Sexual offences equivalent to IPC 376",
         "text": "Section 65 of Bharatiya Nyaya Sanhita 2023 (corresponds to IPC 376): Punishment for rape — Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine. The BNS has broadened the definition with comprehensive categories and enhanced punishments."},
        {"number": "69", "title": "Sexual intercourse by employing deceitful means",
         "text": "Section 69 of Bharatiya Nyaya Sanhita 2023: Sexual intercourse by employing deceitful means — This is a new section not present in the IPC. It criminalizes sexual intercourse obtained through false promise of marriage or employment, making it punishable with imprisonment up to ten years and fine."},
        {"number": "100", "title": "Attempt to murder",
         "text": "Section 100 of Bharatiya Nyaya Sanhita 2023 (equivalent to IPC 307): Attempt to murder — Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment for a term which may extend to ten years, and shall also be liable to fine; and if hurt is caused to any person by such act, the offender shall be liable to imprisonment for life or such punishment as is hereinbefore mentioned."},
        {"number": "303", "title": "Theft equivalent to IPC 378/379",
         "text": "Section 303 of Bharatiya Nyaya Sanhita 2023 (equivalent to IPC 378/379): Theft — Whoever, intending to take dishonestly any moveable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft. Punishment: imprisonment up to three years, or fine, or both. Enhanced punishment for repeat offenders."},
        {"number": "316", "title": "Criminal breach of trust equivalent to IPC 405/406",
         "text": "Section 316 of Bharatiya Nyaya Sanhita 2023 (equivalent to IPC 405/406): Criminal breach of trust — Whoever, being entrusted with property, or with any dominion over property, dishonestly misappropriates or converts to his own use that property, or dishonestly uses or disposes of that property in violation of any direction of law or of any legal contract, commits criminal breach of trust."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Bharatiya Nyaya Sanhita",
        sections=sections,
        year=2023,
        content_type="statute",
    )
    print(f"✅ Bharatiya Nyaya Sanhita 2023 seeded: {result}")
    return result


def seed_bnss():
    """Seed Bharatiya Nagarik Suraksha Sanhita 2023 (replaced CrPC)."""
    sections = [
        {"number": "1", "title": "Short title and commencement",
         "text": "Section 1 of Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023: This Sanhita replaces the Code of Criminal Procedure 1973. It shall come into force on the 1st day of July, 2024. Key changes include mandatory videography of crime scenes, electronic FIR registration, mandatory forensic investigation for serious offences with punishment of 7 years or more, and timelines for investigation completion."},
        {"number": "173", "title": "FIR and information to police (equivalent to CrPC 154)",
         "text": "Section 173 of BNSS 2023 (equivalent to CrPC 154): Every information relating to the commission of a cognizable offence shall be given orally or by electronic communication. The information shall be reduced to writing and signed by the informant. The officer shall give a copy of the information to the informant. Zero FIR concept is now codified — FIR can be filed at any police station regardless of jurisdiction."},
        {"number": "187", "title": "Arrest provisions (equivalent to CrPC 41)",
         "text": "Section 187 of BNSS 2023 (equivalent to CrPC 41): Contains provisions related to arrest. Key changes include mandatory production before magistrate within 24 hours, provision for electronic communication in certain situations, and enhanced protections for women arrested — no woman shall be arrested after sunset and before sunrise except in exceptional circumstances with prior written permission from first class judicial magistrate."},
        {"number": "480", "title": "Plea bargaining provisions",
         "text": "Section 480 of BNSS 2023: Plea bargaining provisions — expanded from CrPC to cover more offences. Available for offences punishable with imprisonment up to 7 years. Provides for mutually satisfactory disposition of the case including compensation to the victim. Not available for offences affecting socio-economic conditions or committed against a woman or a child below 14 years."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Bharatiya Nagarik Suraksha Sanhita",
        sections=sections,
        year=2023,
        content_type="statute",
    )
    print(f"✅ BNSS 2023 seeded: {result}")
    return result


def seed_bsa():
    """Seed Bharatiya Sakshya Adhiniyam 2023 (replaced Evidence Act)."""
    sections = [
        {"number": "1", "title": "Short title and commencement",
         "text": "Section 1 of Bharatiya Sakshya Adhiniyam (BSA) 2023: This Adhiniyam replaces the Indian Evidence Act 1872. It comes into force on 1st July, 2024. Key changes include recognition of electronic and digital evidence, provisions for electronic records as primary evidence, and streamlined rules of evidence."},
        {"number": "57", "title": "Admissibility of electronic records",
         "text": "Section 57 of BSA 2023: Admissibility of electronic or digital record — Any information contained in an electronic record which is printed on paper, stored, recorded or copied in optical or magnetic media or semiconductor memory produced by a computer or communication device shall be deemed to be a document and shall be admissible in evidence without further proof of the original. This is a significant expansion from the old Evidence Act."},
        {"number": "23", "title": "Confession provisions",
         "text": "Section 23 of BSA 2023: Confession caused by inducement, threat or promise, when irrelevant — A confession made by an accused person is irrelevant in a criminal proceeding if the making of the confession appears to the Court to have been caused by any inducement, threat or promise having reference to the charge against the accused person."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Bharatiya Sakshya Adhiniyam",
        sections=sections,
        year=2023,
        content_type="statute",
    )
    print(f"✅ BSA 2023 seeded: {result}")
    return result


def seed_ipc():
    """Seed Indian Penal Code (historical reference)."""
    sections = [
        {"number": "302", "title": "Punishment for murder",
         "text": "Section 302 IPC (Now replaced by BNS Section 63): Punishment for murder — Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. This was one of the most frequently invoked sections of the IPC. Key case: Bachan Singh v. State of Punjab (1980) established the 'rarest of rare' doctrine for death penalty."},
        {"number": "304A", "title": "Causing death by negligence",
         "text": "Section 304A IPC: Causing death by negligence — Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both. This section is frequently applied in cases of road accidents, medical negligence, and industrial accidents."},
        {"number": "376", "title": "Punishment for rape",
         "text": "Section 376 IPC (Now replaced by BNS Section 65): Punishment for rape — Whoever commits rape shall be punished with rigorous imprisonment for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine. Amended after the Nirbhaya case (2012). Criminal Law Amendment Act, 2013 expanded the definition and enhanced punishments."},
        {"number": "420", "title": "Cheating and dishonestly inducing delivery of property",
         "text": "Section 420 IPC: Cheating and dishonestly inducing delivery of property — Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is one of the most commonly invoked sections in fraud cases."},
        {"number": "498A", "title": "Husband or relative of husband of a woman subjecting her to cruelty",
         "text": "Section 498A IPC: Cruelty by husband or relatives — Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine. The Supreme Court in Arnesh Kumar v. State of Bihar (2014) laid down guidelines to prevent misuse of this section."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Indian Penal Code",
        sections=sections,
        year=1860,
        content_type="statute",
    )
    print(f"✅ IPC (historical) seeded: {result}")
    return result


def seed_motor_vehicles_act():
    """Seed Motor Vehicles Act 1988 key sections."""
    sections = [
        {"number": "3", "title": "Necessity for driving licence",
         "text": "Section 3 of Motor Vehicles Act 1988: Necessity for driving licence — No person shall drive a motor vehicle in any public place unless he holds an effective driving licence issued to him authorising him to drive the vehicle. A person under 18 years cannot get a driving licence for motor vehicles (16 years for motorcycles without gear up to 50cc)."},
        {"number": "166", "title": "Application for compensation",
         "text": "Section 166 of Motor Vehicles Act 1988: Application for compensation — An application for compensation arising out of an accident of the nature specified in sub-section (1) of section 165 may be made to the Claims Tribunal. The claim can be filed by the person injured, the owner of the property, or the legal representatives of the deceased."},
        {"number": "185", "title": "Driving by a drunken person or by a person under the influence of drugs",
         "text": "Section 185 of Motor Vehicles Act 1988: Driving by a drunken person — Whoever, while driving, or attempting to drive, a motor vehicle, has, in his blood, alcohol exceeding 30 mg per 100 ml of blood detected in a test by a breath analyser, shall be punishable for the first offence with imprisonment for a term which may extend to six months, or with fine which may extend to ten thousand rupees, or with both. For a second or subsequent offence within three years, imprisonment up to two years or fine up to fifteen thousand rupees or both."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Motor Vehicles Act",
        sections=sections,
        year=1988,
        content_type="statute",
    )
    print(f"✅ Motor Vehicles Act seeded: {result}")
    return result


def seed_consumer_protection():
    """Seed Consumer Protection Act 2019 key sections."""
    sections = [
        {"number": "2", "title": "Definitions",
         "text": "Section 2 of Consumer Protection Act 2019: Definitions — A 'consumer' means any person who buys any goods or hires or avails any service for a consideration which has been paid or promised or partly paid and partly promised, or under any system of deferred payment. The Act covers e-commerce transactions and online purchases."},
        {"number": "35", "title": "Jurisdiction of District Commission",
         "text": "Section 35 of Consumer Protection Act 2019: Jurisdiction of District Commission — Where the value of the goods or services paid as consideration does not exceed one crore rupees, the complaint shall be filed before the District Commission having jurisdiction."},
    ]
    
    result = ingestion_pipeline.ingest_structured_law(
        act_name="Consumer Protection Act",
        sections=sections,
        year=2019,
        content_type="statute",
    )
    print(f"✅ Consumer Protection Act seeded: {result}")
    return result


def seed_all_laws():
    """Seed all pre-packaged laws."""
    print("🏛️ Seeding Indian Legal Database...")
    results = []
    results.append(seed_constitution())
    results.append(seed_bns())
    results.append(seed_bnss())
    results.append(seed_bsa())
    results.append(seed_ipc())
    results.append(seed_motor_vehicles_act())
    results.append(seed_consumer_protection())
    print("✅ All laws seeded successfully!")
    return results


if __name__ == "__main__":
    seed_all_laws()
