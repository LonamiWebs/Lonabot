from re import split


class NumberHelper:
    __known_word_to_int = {
        'a': 1,  # Consider 'a' as 1 (i.e., a hundred)
        'zero': 0, 'ten': 10,
        'one': 1, 'eleven': 11,
        'two': 2, 'twelve': 12, 'twenty': 20,
        'three': 3, 'thirteen': 13, 'thirty': 30,
        'four': 4, 'fourteen': 14, 'forty': 40,
        'five': 5, 'fifteen': 15, 'fifty': 50,
        'six': 6, 'sixteen': 16, 'sixty': 60,
        'seven': 7, 'seventeen': 17, 'seventy': 70,
        'eight': 8, 'eighteen': 18, 'eighty': 80,
        'nine': 9, 'nineteen': 19, 'ninety': 90,

        # Also handle these cases
        'once': 1, 'twice': 2,

        'fourty': 40  # Common typo
    }

    @staticmethod
    def get_int(literal):
        """
        Converts a literal integer (as string) to an integer value.
        Note that this will trim any decimal places.

        :param literal: The literal string to convert
        :return: The integer value
        """

        # Fix our string if necessary
        literal = literal.strip()

        # First try a normal string → int conversion
        try:
            # We're working with integers, not floating point numbers
            if '.' in literal:
                literal = literal[:literal.index('.')]
            if ',' in literal:
                literal = literal[:literal.index(',')]

            return int(literal)

        except ValueError:
            # Let's do a normal conversion

            # If it's a known-value, return it straightforward!
            if literal in NumberHelper.__known_word_to_int:
                return NumberHelper.__known_word_to_int[literal]

            # Else, let's go digit by digit
            words = split('\W+', literal)  # Split by everything which isn't a letter
            digits = []

            # Was the last digit multi-digit (> 9)
            last_multi_digit = False

            for word in words:

                word = word.lower()
                if word == 'point':  # Stop (truncate)
                    break

                # If it's a known digit, append it to the list
                if word in NumberHelper.__known_word_to_int:
                    number = NumberHelper.__known_word_to_int[word]

                    # If the last digit was multi digit, and the later is single digit
                    # (< 10), we want to sum them. For example: eighty three hundred
                    if last_multi_digit:
                        digits[-1] += number
                    else:
                        digits.append(number)

                    # Then update the status
                    if number > 9:
                        last_multi_digit = True
                    else:
                        last_multi_digit = False

                else:
                    last_multi_digit = False  # Clear state

                    # Else, it may be a "modifier" (i.e., one *thousand*)
                    # In this case, modify the last added digit
                    if len(digits) > 0:
                        if word == 'trillion':
                            digits[-1] *= 1000000000000
                        elif word == 'billion':
                            digits[-1] *= 1000000000
                        elif word == 'million':
                            digits[-1] *= 1000000
                        elif word == 'thousand':
                            digits[-1] *= 1000
                        elif word == 'hundred':
                            digits[-1] *= 100

            # Then just sum all the digits together
            if words[0] == 'negative':
                return -sum(digits)
            else:
                return sum(digits)
