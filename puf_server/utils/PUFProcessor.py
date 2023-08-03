from collections import Counter
import csv
import statistics


class PUFProcessor:
    def __init__(self):
        pass

    @staticmethod
    def calculate_ones_and_zeros_initialValue(response, initialValue):
        """ Parses the 8-bit values stored in the measurement array and returns the number of zeros and ones.

        :param response:
        :return:
        """
        ones = 0
        zeros = 0
        gaps = 0
        for x in response:
            if x == int(initialValue.replace('0x', ''), 16):
                ones = ones + 1
            elif x == -1:
                gaps = gaps + 1
            else:
                zeros = zeros + 1
        '''ones = sum(1 for x in response if x == int(
            initialValue.replace('0x', ''), 16))
        zeros = sum(1 for x in response if x != int(
            initialValue.replace('0x', ''), 16))'''
        return ones, zeros, gaps

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
        l = len(response1)
        sum = 0
        for c1, c2 in zip(response1, response2):
            if c1 == -1 or c2 == -1:
                l = l-1
            else:
                if c1 != c2:
                    sum = sum + 1

        return 1 - sum / l

    @staticmethod
    def calculate_inter_hd(response1, response2):
        if len(response1) != len(response2):
            raise ValueError("Responses must have equal length.")

        l = len(response1)
        hd = PUFProcessor.hamming_distance(response1, response2)

        return hd

    @staticmethod
    def read_and_store_input_data(input_file, startAddress, stopAddress):
        """ Reads a csv file and transforms it an array consisting of the address and the corresponding value.

        :param input_file: Input file to parse.
        :param startAdress, stopAddress: Size of the filled memory, required to fill gaps with -1.
        :return: response as array
        """

        input_file_path = remove_first_slash(input_file)

        detected_delimiter = determine_csv_delimiter(input_file_path)
        array_to_store = []

        with open(input_file_path) as csvfile:
            file_reader = csv.reader(
                csvfile, delimiter=detected_delimiter, quotechar='\n')

            # Skip the header row
            next(file_reader)

            current_address = startAddress

            for row in file_reader:
                if isinstance(row[0], (str, bytes)):
                    if row[0][0:2] == '0x':
                        address = int(row[0].replace('0x', ''), 16)
                    else:
                        address = int(row[0])

                if row[1][0:2] == '0x':
                    value = int(row[1].replace('0x', ''), 16)
                else:
                    value = int(row[1], 16)

                # print(address, value)
                if address == current_address:
                    array_to_store.append(value)
                    current_address = current_address + 1
                else:
                    for _ in range(current_address, address):
                        array_to_store.append(-1)
                    array_to_store.append(value)
                    current_address = address + 1

            if current_address < stopAddress:
                for _ in range(current_address, stopAddress):
                    array_to_store.append(-1)

        return array_to_store

    @staticmethod
    def calculate_ones_and_zeros(input_data):
        """ Parses the 8-bit values stored in the measurement array and returns the number of zeros and ones.

        :param input_data:
        :return:
        """
        ones = 0
        zeros = 0
        gaps = 0
        for data in input_data:
            if data == -1:
                gaps += 1
            else:
                ret = PUFProcessor.get_ones_and_zeros_in_byte(data)
                ones += ret[0]
                zeros += ret[1]
        return ones, zeros, gaps

    @staticmethod
    def get_ones_and_zeros_in_byte(value):
        """

        :param value:
        :return:
        """
        one_ctr = 0
        for i in range(8):
            if (pow(2, i) & value) != 0:
                one_ctr += 1

        return one_ctr, 8 - one_ctr


'''
the determine_csv_delimiter function takes the file path as input. 
It opens the CSV file, reads the first line , and initializes
an empty dictionary to store the counts of each potential delimiter.
Finally, it determines the delimiter with the highest count by using 
the max function on the delimiter_counts dictionary and selecting 
the key with the highest value.
'''


def determine_csv_delimiter(file_path):
    with open(file_path, 'r') as csv_file:
        first_line = csv_file.readline()
        # List of potential delimiters to check
        delimiters = [',', ';', '\t']  # Add more delimiters if needed

        # Dictionary to store delimiter counts
        delimiter_counts = {}

        # Count the occurrences of each delimiter in the first line
        for delimiter in delimiters:
            count = first_line.count(delimiter)
            delimiter_counts[delimiter] = count

        # Determine the delimiter with the highest count
        most_common_delimiter = max(delimiter_counts, key=delimiter_counts.get)

    return most_common_delimiter


def remove_first_slash(path):
    if path.startswith('/'):
        path = path.lstrip('/')
    return path
