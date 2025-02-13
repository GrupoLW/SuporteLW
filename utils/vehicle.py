import re
class Vehicle:

    def __init__(self, plate, renavam, chassi):
        self._plate_given = plate
        self.inverted_plate = ''
        self.plate_old_pattern = ''
        self.plate_mercosul_pattern = ''
        self._renavam = renavam
        self._chassi = chassi
        self._uf = None

    def __str__(self):
        return f'Placa: {self._plate_given}'

    @classmethod
    def create_through_plate(cls, plate):
        clean_plate = cls.clean_data(plate)
        vehicle_with_plate = cls(clean_plate, None, None)
        vehicle_with_plate.reverse_the_plate_pattern()
        vehicle_with_plate.save_the_plate_patterns()
        return vehicle_with_plate

    @classmethod
    def create_through_renavam(cls, renavam):
        clean_renavam = cls.clean_data(renavam)
        vehicle_with_renavam = cls(None,clean_renavam, None)
        return vehicle_with_renavam

    @classmethod
    def create_through_chassi(cls, chassi):
        clean_chassi = cls.clean_data(chassi)
        vehicle_with_chassi = cls(None, None, clean_chassi)
        return vehicle_with_chassi

    @property
    def plate_given(self):
        return self._plate_given

    @plate_given.setter
    def plate_given(self, plate):
        clean_plate = self.clean_data(plate)
        self._plate_given = clean_plate
        self.reverse_the_plate_pattern()
        self.save_the_plate_patterns()

    @property
    def renavam(self):
        return self._renavam

    @renavam.setter
    def renavam(self, renavam):
        self._renavam = self.clean_data(renavam)


    @staticmethod
    def renavam_with_11_digits(renavam):
        if renavam is not None:
            renavam = renavam.strip()

        if renavam == '' or renavam is None:
            return None
        elif len(renavam) >= 5:
            return renavam.zfill(11)
        else:
            return renavam
        

    @property
    def chassi(self):
        return self._chassi

    @chassi.setter
    def chassi(self, chassi):
        self._chassi = self.clean_data(chassi)

    @property
    def uf(self):
        return self._uf

    @uf.setter
    def uf(self, uf):
        self._uf = self.clean_data(uf)


    @staticmethod
    def clean_data(data : str):
        return data.strip().upper().replace('-', '')


    @staticmethod
    def test_the_plate(plate_given):
        clean_plate = Vehicle.clean_data(plate_given)
        if len(clean_plate) != 7:
            return False
        elif Vehicle.is_old_pattern(clean_plate) or Vehicle.is_mercosul_pattern(clean_plate):
            return True
        else:
            return False

    @staticmethod
    def is_old_pattern(plate):
        old_pattern = r'^[A-Z]{3}\d{4}$'
        return re.match(old_pattern, plate)

    @staticmethod
    def is_mercosul_pattern(plate):
        mercosul_pattern = r'^[A-Z]{3}\d[A-Z]\d{2}$'
        return re.match(mercosul_pattern, plate)

    @property
    def fifth_digit_value(self):
        return self._plate_given[4]


    def reverse_the_fifth_digit_value(self):
        conversion_table = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4,
            'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9
        }
        fifth_digit = self.fifth_digit_value
        if Vehicle.is_mercosul_pattern(self._plate_given):
            return conversion_table[fifth_digit]
        elif Vehicle.is_old_pattern(self._plate_given):
            for key, value in conversion_table.items():
                if value == int(fifth_digit):
                    return key
        else:
            return None

    def reverse_the_plate_pattern(self):
        if Vehicle.test_the_plate(self._plate_given):
            self.inverted_plate = self._plate_given[:4] + str(self.reverse_the_fifth_digit_value()) + self._plate_given[5:]


    def save_the_plate_patterns(self):
        if Vehicle.is_mercosul_pattern(self._plate_given):
            self.plate_mercosul_pattern = self._plate_given
            self.plate_old_pattern = self.inverted_plate
        else:
            self.plate_old_pattern = self._plate_given
            self.plate_mercosul_pattern = self.inverted_plate


    @staticmethod
    def static_reverse_the_plate_pattern(plate):
        clean_plate = Vehicle.clean_data(plate)
        if Vehicle.test_the_plate(clean_plate):
            return clean_plate[:4] + str(Vehicle.static_reverse_the_fifth_digit_value(clean_plate)) + clean_plate[5:]
        return ''
    

    @staticmethod
    def static_reverse_the_fifth_digit_value(plate):
        conversion_table = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4,
            'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9
        }
        fifth_digit = plate[4]
        if Vehicle.is_mercosul_pattern(plate):
            if fifth_digit in conversion_table:
                return  conversion_table[fifth_digit]
            else:
                return ''
        elif Vehicle.is_old_pattern(plate):
            for key, value in conversion_table.items():
                if value == int(fifth_digit):
                    return key
        else:
            return ''