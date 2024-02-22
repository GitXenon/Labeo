import unittest

from openai_tts import replace_numbers, cloze_remover

class TestReplaceNumbers(unittest.TestCase):
    def test_normal_case(self):
        text = "Ich habe 3 Äpfel in meiner Tasche."
        expected_output = "Ich habe drei Äpfel in meiner Tasche."
        self.assertEqual(replace_numbers(text), expected_output)

    def test_money_case_euro(self):
        text = "Er hat 100 Euro von seinem Teilzeitjob verdient."
        expected_output = "Er hat einhundert Euro von seinem Teilzeitjob verdient."
        self.assertEqual(replace_numbers(text), expected_output)

    def test_money_case_dollar(self):
        text = "Das Hotelzimmer kostet 150 Dollar pro Nacht."
        expected_output = "Das Hotelzimmer kostet einhundertfünfzig Dollar pro Nacht."
        self.assertEqual(replace_numbers(text), expected_output)

    def test_combined_case(self):
        text = "Der preis einer Apfel beträgt 0,36 Euro oder 0,56 Euro."
        expected_output = "Der preis einer Apfel beträgt null Komma drei sechs Euro oder null Komma fünf sechs Euro."
        self.assertEqual(replace_numbers(text), expected_output)

    def test_no_numbers(self):
        text = "Das ist ein einfacher Text."
        self.assertEqual(replace_numbers(text), text)

    def test_money_with_comma(self):
        text = "Der Preis einer Banane beträgt 0,79 Euro."
        expected_output = "Der Preis einer Banane beträgt null Komma sieben neun Euro."
        self.assertEqual(replace_numbers(text), expected_output)

    def test_money_with_comma(self):
        text = "Die Schokolade kostet 1,99 Euro pro Tafel."
        expected_output = "Die Schokolade kostet eins Komma neun neun Euro pro Tafel."
        self.assertEqual(replace_numbers(text), expected_output)

class TestClozeRemover(unittest.TestCase):
    def test_multiple_cloze(self):
        text = "Wir {{c1::brauchen::besoin}} {{c2::einen}} Regenschirm."
        expected_output = "Wir brauchen einen Regenschirm."
        self.assertEqual(cloze_remover(text), expected_output)

        text = "{{c1::Bist du Künstler(in)?}} {{c2::Ja, ich bin Künstler(in).}} {{c3::Und was machst du als Künstler(in)?}} {{c4::Ich male Bilder.}}"
        expected_output = "Bist du Künstler(in)? Ja, ich bin Künstler(in). Und was machst du als Künstler(in)? Ich male Bilder."
        self.assertEqual(cloze_remover(text), expected_output)

        text = "{{c1::Ursprünglich::À l'origine}} waren diese Bonbons gar nicht so {{c2::süß::sucrés}}, wie wir sie heute kennen."
        expected_output = "Ursprünglich waren diese Bonbons gar nicht so süß, wie wir sie heute kennen."
        self.assertEqual(cloze_remover(text), expected_output)

        text = "Wann {{c1::fängt::tackle something, start with something}} die Telekonferenz {{c1::an}}?"
        expected_output = "Wann fängt die Telekonferenz an?"
        self.assertEqual(cloze_remover(text), expected_output)

    def test_one_cloze(self):
        text = "Ihr {{c1::könnt::können}} mich später anrufen."
        expected_output = "Ihr könnt mich später anrufen."
        self.assertEqual(cloze_remover(text), expected_output)

        text = "Der WLAN-Code {{c1::steht::se trouve/figure}} auf der Zimmerkarte."
        expected_output = "Der WLAN-Code steht auf der Zimmerkarte."
        self.assertEqual(cloze_remover(text), expected_output)

        text = "Hast du {{c1::schon::déjà}} gefrühstückt?"
        expected_output = "Hast du schon gefrühstückt?"
        self.assertEqual(cloze_remover(text), expected_output)

    def test_no_cloze(self):
        text = "Was sind die Arbeitstage?"
        self.assertEqual(cloze_remover(text), text)

        text = "Paul will im Januar auf die Kanarischen Inseln fliegen."
        self.assertEqual(cloze_remover(text), text)

    def test_empty_string(self):
        text = ""
        self.assertEqual(cloze_remover(text), text)

    def test_string_with_only_cloze(self):
        text = "{{c1::Test}}"
        expected_output = "Test"
        self.assertEqual(cloze_remover(text), expected_output)

    @unittest.expectedFailure
    def test_nested_cloze(self):
        text = "{{c1::Outer {{c2::inner}} cloze}}"
        expected_output = "Outer inner cloze"
        self.assertEqual(cloze_remover(text), expected_output)

    def test_non_ascii_characters(self):
        text = "{{c1::Bücher}}"
        expected_output = "Bücher"
        self.assertEqual(cloze_remover(text), expected_output)

    def test_special_characters(self):
        text = "{{c1::Test!}}"
        expected_output = "Test!"
        self.assertEqual(cloze_remover(text), expected_output)

if __name__ == '__main__':
    unittest.main()