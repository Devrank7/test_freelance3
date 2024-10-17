from abc import ABC, abstractmethod


class PDFConverterText(ABC):
    @abstractmethod
    def convert_pdf(self) -> str:
        pass


class PDFConverterFreelance(PDFConverterText):

    def __init__(self, original_text: str):
        self.original_text = original_text

    required_keys = ['Версия PDF', 'Линеаризация', 'Дата редактирования',
                     'Создатель', 'Дата оцифровки', 'Производитель',
                     'Тегированный PDF Язык', 'Количество страниц']

    def convert_pdf(self) -> str:
        lines = self.original_text.splitlines()
        data_dict = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data_dict[key.strip()] = value.strip()
        if not all(key in data_dict for key in self.required_keys):
            raise ValueError("Некорректный PDF: отсутствуют необходимые ключи.")
        new_text = (
            f"---- PDF ----\n"
            f"Версия PDF : {data_dict['Версия PDF']}\n"
            f"Линеаризация : {data_dict['Линеаризация']}\n"
            f"Дата редактирования : {data_dict['Дата редактирования']}\n"
            f"Создатель : {data_dict['Создатель']}\n"
            f"Дата оцифровки : {data_dict['Дата оцифровки']}\n"
            f"Производитель : {data_dict['Производитель']}\n"
            f"Тегированный PDF Язык : {data_dict['Тегированный PDF Язык']}\n"
            f"Количество страниц : {data_dict['Количество страниц']}\n"
        )
        return new_text


def convert_text_from_pdf(pdf_strategy: PDFConverterText) -> str:
    return pdf_strategy.convert_pdf()
