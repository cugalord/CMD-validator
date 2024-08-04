import CDMparser
import PUML
import Validation
import ErrorLog
import os


def normal_validation_mode(src_model_path, solution_model_path, puml_mode):
    """
    normal_validation_mode function is used to parse the source and solution model, validate the source model against the solution model,
    and write the source model to a PlantUML file.
    """
    try:
        # Define the path of the output PlantUML file
        output_path = os.path.splitext(src_model_path)[0] + ".puml"

        # Parse the source and solution models
        src_model = CDMparser.CDMParser(src_model_path)
        src_model = src_model.get_main_model()

        solution_model = CDMparser.CDMParser(solution_model_path)
        solution_model = solution_model.get_main_model()

        # Validate the source model against the solution model
        validation = Validation.Validation(src_model, solution_model)
        validation.validate()

        # Write the source model to a PlantUML file
        puml = PUML.PUML(puml_mode)
        puml.write_model(output_path, src_model, validation.error_log)

    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except IOError as e:
        print(f"IO error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def batch_verification_mode(directory_path, solution_model_path, puml_mode):
    """
    Function to read all the files from the specified directory and validate them.
    """
    # Iterate over all files in the directory
    try:
        for filename in os.listdir(directory_path):
            # Construct the full file path
            if os.path.splitext(filename)[1] == ".cdm":
                file_path = os.path.join(directory_path, filename)
                normal_validation_mode(file_path, solution_model_path, puml_mode)
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except IOError as e:
        print(f"IO error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    # Uncomment the function you want to run
    src_model_path = "W:/Diplomsko delo/Diploma/tests/conceptual_tasks/video_shop/solution.cdm"
    solution_model_path = "W:/Diplomsko delo/Diploma/tests/conceptual_tasks/video_shop/Primer 2.cdm"

    normal_validation_mode(src_model_path, solution_model_path, "PNG")
    #puml_test()
    #validator_test()
