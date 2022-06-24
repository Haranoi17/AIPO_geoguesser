from language_detection import LanguageIdentification

if __name__ == "__main__":
    test = "to jest testowy tekst"
    testENG = "a mountain road"
    testPor = "Olá amigos"
    testIT = "sto per andare"

    # default -> large model
    LANGUAGE = LanguageIdentification()
    print(LANGUAGE.get_country(test))
    print(LANGUAGE.get_country(testENG))
    print(LANGUAGE.get_country(testPor))
    print(LANGUAGE.get_country(testIT))

    print("------SMALL MODEL --------")
    # small model -> low acc
    LANGUAGE_SMALL = LanguageIdentification(large_model=False)
    print(LANGUAGE_SMALL.get_country(test))
    print(LANGUAGE_SMALL.get_country(testENG))
    print(LANGUAGE_SMALL.get_country(testPor))
    print(LANGUAGE_SMALL.get_country(testIT))