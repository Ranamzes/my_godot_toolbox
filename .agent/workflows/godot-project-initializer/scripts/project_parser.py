import os
import re

class GodotConfigParser:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.sections = {} # {section_name: {key: value}}
        self.section_order = [] # Список для сохранения исходного порядка секций
        self.section_comments = {} # Комментарии и пустые строки {section_name_or_global: [lines]}
        self.key_order = {} # {section_name: [key_names]}
        
        if filepath and os.path.exists(filepath):
            self.read(filepath)

    def read(self, filepath):
        current_section = None
        current_comments = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                
                # Сохраняем пустые строки и комментарии
                if not stripped or stripped.startswith(';'):
                    current_comments.append(line)
                    continue
                
                # Парсинг секции: [section]
                section_match = re.match(r'^\[([\w./]+)\]$', stripped)
                if section_match:
                    current_section = section_match.group(1)
                    if current_section not in self.sections:
                        self.sections[current_section] = {}
                        self.section_order.append(current_section)
                        self.key_order[current_section] = []
                    
                    if current_comments:
                        self.section_comments[current_section] = current_comments
                        current_comments = []
                    continue
                
                # Парсинг ключа-значения: key=value
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    
                    if current_section is None:
                        # Глобальные настройки до первой секции (например, config_version)
                        global_sec = '_global'
                        if global_sec not in self.sections:
                            self.sections[global_sec] = {}
                            self.section_order.append(global_sec)
                            self.key_order[global_sec] = []
                        current_section = global_sec
                    
                    self.sections[current_section][key] = val
                    if key not in self.key_order[current_section]:
                        self.key_order[current_section].append(key)
                        
                    if current_comments:
                        # Привязываем комментарии к ключу, если нужно (упростим: просто сохраняем)
                        current_comments = []

    def set_value(self, section, key, value):
        """Устанавливает значение для ключа в секции. Создает секцию/ключ при отсутствии."""
        if section not in self.sections:
            self.sections[section] = {}
            self.section_order.append(section)
            self.key_order[section] = []
            
        self.sections[section][key] = str(value)
        if key not in self.key_order[section]:
            self.key_order[section].append(key)

    def get_value(self, section, key, default=None):
        if section in self.sections and key in self.sections[section]:
            return self.sections[section][key]
        return default

    def merge_packed_array(self, section, key, new_elements):
        """Сливает элементы в PackedStringArray, предотвращая дубликаты."""
        current_val = self.get_value(section, key)
        elements = set()
        
        if current_val:
            # Извлекаем элементы из PackedStringArray("elem1", "elem2")
            match = re.match(r'^PackedStringArray\((.*)\)$', current_val)
            if match:
                raw_elems = match.group(1).strip()
                if raw_elems:
                    # Разделяем по запятым, учитывая кавычки
                    for part in re.split(r',\s*', raw_elems):
                        part = part.strip().strip('"').strip("'")
                        if part:
                            elements.add(part)
        
        # Добавляем новые элементы
        for elem in new_elements:
            elements.add(elem)
            
        # Формируем новую строку
        sorted_elements = sorted(list(elements))
        array_str = f'PackedStringArray(' + ', '.join(f'"{el}"' for el in sorted_elements) + ')'
        self.set_value(section, key, array_str)

    def merge_with_ini(self, other_filepath):
        """Интегрирует настройки из другого INI-подобного файла."""
        other = GodotConfigParser(other_filepath)
        for section, keys in other.sections.items():
            for key, val in keys.items():
                if val.startswith('PackedStringArray('):
                    # Извлекаем элементы для слияния массивов
                    match = re.match(r'^PackedStringArray\((.*)\)$', val)
                    if match:
                        raw_elems = match.group(1).strip()
                        elems = []
                        if raw_elems:
                            elems = [el.strip().strip('"').strip("'") for el in re.split(r',\s*', raw_elems)]
                        self.merge_packed_array(section, key, elems)
                else:
                    self.set_value(section, key, val)

    def write(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            for section in self.section_order:
                # Записываем сохраненные комментарии перед секцией
                if section in self.section_comments:
                    for comment in self.section_comments[section]:
                        f.write(comment)
                
                # Записываем заголовок секции (кроме виртуальной _global)
                if section != '_global':
                    f.write(f'[{section}]\n')
                
                # Записываем ключи и значения
                for key in self.key_order[section]:
                    val = self.sections[section][key]
                    f.write(f'{key}={val}\n')
                
                f.write('\n') # Пустая строка между секциями
