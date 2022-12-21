from django.test import SimpleTestCase
import random

from social_media.screening.screening_modules.confidentialinformationscreener import ConfidentialInformationScreener


class MyTestCase(SimpleTestCase):
    def test_extraction(self):
        test_numbers = [
            # IBAN
            'UA374108274369263543890221494',
            'BY 25 178642 877193 2823 0583 1147',
            'RU 02 0445-2560-0407-02-810412345-678901',

            # CARD NUMBERS
            '4929851632491839',
            '5340 7010 3650 8191',
            '5351-0817-2556-1116',

            # PHONE NUMBERS
            '+375(17)237-21-52',
            '+375151252704',
            '+375 154 114 6628',
            '+7 401 635 1620',
            '04016301503',
            '+7(401) 189-6869',
            '+380 44 659 1724',
            '+380(062)53-64-77',
            '+380 (0629) 23-42-86',
            '044 406-61-84'
        ]
        random.shuffle(test_numbers)

        test_case = """Some multi line string with a phone numbers papered around: Lorem ipsum dolor sit amet, 
        consectetur adipiscing elit. {} In in convallis turpis, sed tempus magna. Sed malesuada et 
        diam vel interdum. Fusce ac mi sagittis,  tristique orci eu, tristique augue. Praesent lacinia 
        vitae ex ut commodo. Integer leo neque, volutpat {} vitae tortor et, lobortis tempus tortor. 
        Nunc ex orci, interdum tempor urna ac, consequat porta lorem. Vivamus tempus nulla a tortor hendrerit 
        hendrerit. Etiam {} tristique aliquet est sed interdum. Pellentesque a viverra velit. Sed eget 
        enim tempus dui tempor facilisis. Sed in tellus at urna porttitor volutpat vitae quis magna. Praesent 
        fringilla sollicitudin ex, {} ut fermentum lacus {} dapibus at. Aliquam tincidunt eget nibh vitae 
        lacinia. Aliquam quis malesuada enim, non efficitur mauris. Curabitur at lorem vel nisl placerat faucibus et 
        sit amet nisl. Quisque id enim rutrum, lobortis erat vitae, mattis sapien. Sed facilisis nibh lacinia leo 
        dignissim cursus. Aenean ac arcu consectetur, rutrum neque quis, elementum ligula. Sed eget sem ornare orci 
        cursus lobortis. Proin {} sit amet arcu at est vehicula {} efficitur. {} Vivamus tristique lacus 
        neque, sed finibus nunc accumsan sed. Phasellus consectetur cursus lobortis. Pellentesque tristique pharetra 
        arcu, non {} venenatis est placerat eu. Integer varius sollicitudin nunc at sollicitudin. Donec venenatis 
        sollicitudin ligula, pulvinar vehicula neque volutpat nec. {} Integer ut finibus elit. Curabitur egestas sed 
        felis at finibus. Proin ullamcorper fringilla tristique. Fusce tincidunt nunc ac magna facilisis, ac molestie 
        sapien auctor. Duis at tortor eget diam accumsan porttitor. Nam efficitur libero quam, in bibendum augue 
        ultricies rutrum. Aliquam {} erat volutpat. In congue diam sed lorem sodales congue. Cras tincidunt feugiat 
        ultricies. Sed pharetra urna sit amet facilisis semper. Fusce ac elit in velit tincidunt ornare. Sed quis 
        arcu malesuada, tincidunt justo at, sodales quam. Etiam est lacus, placerat nec ex sed, volutpat auctor 
        turpis. Sed pellentesque augue  {} odio, et sollicitudin nunc lobortis quis. Sed {} malesuada rutrum nisi, 
        ac tristique {} sem iaculis vel. Maecenas lobortis lacus ac turpis pellentesque lacinia. Donec luctus felis nec 
        est hendrerit posuere. Ut maximus erat urna, quis imperdiet ex consectetur nec. Curabitur ultricies purus sit 
        amet finibus vestibulum. Mauris vel semper nibh. Aenean sapien arcu, fringilla {} vitae purus ac, 
        tempus malesuada felis. Sed sollicitudin dolor a lorem fringilla, vel venenatis erat ultrices. Ut dignissim, 
        orci et pulvinar ultrices, ipsum {} dui finibus massa, vel ornare diam arcu nec libero. Duis pulvinar odio quis 
        elementum semper. Nam id tortor mi. Aenean tellus nunc, imperdiet at porta ac, commodo sit amet sapien. Nunc 
        accumsan lectus a suscipit sagittis. Etiam quis consequat urna. """.format(*test_numbers)

        screener = ConfidentialInformationScreener()
        extraction_results = screener.look_for_info(test_case)
        result = []
        for item in extraction_results:
            result.append(item.item)

        self.assertCountEqual(test_numbers, result)

