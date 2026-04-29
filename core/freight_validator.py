import binascii

class FreightValidator:
    @staticmethod
    def generate_hex_code(text):
        """Genera un código hexadecimal a partir de un texto (ej. ID de viaje o carga)"""
        return text.encode('utf-8').hex()

    @staticmethod
    def hex_to_bin(hex_code):
        """Transforma el código hexadecimal a binario (para cuando el viaje está en curso)"""
        try:
                                                                                  
                                                                              
            scale = 16
            num_of_bits = len(hex_code) * 4
            bin_code = bin(int(hex_code, scale))[2:].zfill(num_of_bits)
            return bin_code
        except Exception as e:
            return None

    @staticmethod
    def bin_to_hex(bin_code):
        """Transforma de nuevo el binario a hexadecimal (al llegar al destino)"""
        try:
                                                                              
            hex_code = hex(int(bin_code, 2))[2:]
                                                                        
            if len(hex_code) % 2 != 0:
                hex_code = '0' + hex_code
            return hex_code
        except Exception as e:
            return None

    @staticmethod
    def validate_arrival(original_hex, current_bin):
        """
        Valida que el código binario actual en tránsito coincida con el hex original.
        Simula la 'validación de dos puntos' (Punto A vs Punto B).
        """
        converted_back_hex = FreightValidator.bin_to_hex(current_bin)
        return original_hex.lower() == converted_back_hex.lower(), converted_back_hex
