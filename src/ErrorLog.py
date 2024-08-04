

class Error:
    """
    The Error class represents an error that occurred during the execution of the program. It contains information
    about the type of object that caused the error, the id and name of the object, the type of error, and a message
    describing the error.
    """
    def __init__(self, TypeOfObject, id, name, TypeOfError, message):
        """
                Initialize the Error class with the type of object that caused the error, the id and name of the object, the type of error, and a message describing the error.

                :param TypeOfObject: The type of object that caused the error.
                :param id: The id of the object that caused the error.
                :param name: The name of the object that caused the error.
                :param TypeOfError: The type of error that occurred.
                :param message: A message describing the error.
        """
        self.type = TypeOfObject
        self.id = id
        self.name = name
        self.error = TypeOfError
        self.message = message


class ErrorLog:
    """
        The ErrorLog class is used to log the errors that occur during the execution of the program.
        It contains a list of Error objects.
    """
    def __init__(self):
        """
                Initialize the ErrorLog class and create an empty list of errors.
        """
        self.errors: list[Error] = []

    def find_error(self, object_id):
        """
               Find an error in the error log based on the id of the object that caused the error.

               :param object_id: The id of the object that caused the error.
               :return: The Error object and a boolean indicating whether the error was found.
        """
        for error in self.errors:
            if error.id == object_id:
                return error, True
        return None, False

    def add_error(self, TypeOfObject, object_id, name, TypeOfError, message):
        """
                Add an error to the error log.

                :param TypeOfObject: The type of object that caused the error.
                :param object_id: The id of the object that caused the error.
                :param name: The name of the object that caused the error.
                :param TypeOfError: The type of error that occurred.
                :param message: A message describing the error.
        """
        self.errors.append(Error(TypeOfObject, object_id, name, TypeOfError, message))

    def prt(self):
        """
                Print the messages of all the errors in the error log.

                :return: An empty string.
        """
        str_build= ""
        for error in self.errors:
            print(error.message)
        return str_build
