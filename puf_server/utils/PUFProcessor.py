
import csv

class PUFProcessor:
    def __init__(self):
        pass

    @staticmethod
    def calculate_ones_and_zeros(response):
        """ Parses the 8-bit values stored in the measurement array and returns the number of zeros and ones.

        :param input_data:
        :return:
        """
        ones = sum(1 for x in response if x == 1)
        zeros = sum(1 for x in response if x == 0)
        return ones, zeros
    
    @staticmethod
    def hamming_weight(response):
        """Calculates the Hamming weight of a PUF response."""
        return sum(bit for bit in response)/len(response)

    @staticmethod
    def hamming_distance(response1, response2):
        """Calculates the Hamming distance of two PUF responses."""
        # Ensure that both responses have the same length
        if len(response1) != len(response2):
            raise ValueError("PUF responses must have the same length")

        # Calculate and return the Hamming distance
        return sum(c1 != c2 for c1, c2 in zip(response1, response2))

   
    
    @staticmethod
    def read_and_store_input_data(input_file):
        """ Reads a csv file and transforms it an array consisting of the address and the corresponding value.

        :param input_file: Input file to parse.
        :param memory_size: Size of the memory, required to fill gaps with -1.
        :return: list of measurements
        """
        with open(input_file) as csvfile:
            file_reader = csv.reader(csvfile, delimiter=',', quotechar='\n')

            # Skip the header row
            next(file_reader)

            array_to_store = [int(row[1]) for row in file_reader]
                
        return array_to_store