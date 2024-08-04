from plantuml import PlantUML
import CDMmodel
import ErrorLog
import os
from os.path import abspath

"""
        The PUML class is used to write a model to a file in PlantUML format and then process it to an image.
        It uses the PlantUML library to process the file to an image.
"""


class PUML:
    def __init__(self, mode):
        """
        Initialize the PUML class and set up the PlantUML server and styles for different elements and statuses.

        :param mode: A string that determines the output format of the PlantUML server.
                     If "PNG", the server will output PNG images. Otherwise, it will output SVG images.
        """
        self.mode = mode
        if mode == "PNG":
            self.server = PlantUML(url='http://www.plantuml.com/plantuml/img/', basic_auth={}, form_auth={},
                                   http_opts={}, request_opts={})
        else:
            self.server = PlantUML(url='http://www.plantuml.com/plantuml/svg/', basic_auth={}, form_auth={},
                                   http_opts={}, request_opts={})

        # styles for different elements and statuses to be used in the model
        self.style = {
            "entity_ok": "#ffffff/b0ffff;line:00aaaa",
            "entity_error": "#FF0000;line:000000",

            "association_ok": "#ffffff/d0d0ff;line:8080ff",
            "association_error": "#FF0000;line:000000",

            "inheritance_ok": "#ffffff/b0ffff;line:8080ff",
            "inheritance_error": "#FF0000;line:000000",

            "inheritance_link_ok": "#8080ff",
            "inheritance_link_error": "#FF0000",

            "relationship_ok": "#8080ff",
            "relationship_error": "#FF0000",

            "package_ok": "#ffffff/ffffc0;line:b2b2b2"
        }

    def write_model(self, path: str, model: CDMmodel.Model, error_log: ErrorLog):
        """
                Write a model to a file in PlantUML format, correct the file, and process it to an image.

                :param path: The path to the output PlantUML file.
                :param model: The model to be written to the file.
                :param error_log: The error log for the model.
        """
        e_msg = ""
        for error in error_log.errors:
            e_msg += f"{error.message} \n"

        model_str = f"@startuml  \n hide cirlcle \n title {model.name} \n"
        if e_msg == "":
            message = f'legend top left \n no errors \n end legend'
        else:
            message = f'legend top left \n {e_msg} \n end legend'

        tables = []
        for table in model.entities:
            if error_log.find_error(table.id)[1]:
                tables.append(table.puml(self.style["entity_error"]))
            else:
                tables.append(table.puml(self.style["entity_ok"]))

        # association and association links
        associations = []
        for association in model.associations:
            if error_log.find_error(association.id)[1]:
                associations.append(association.puml(self.style["association_error"]))
            else:
                associations.append(association.puml(self.style["association_ok"]))

        associations_links = []
        for association_link in model.association_links:
            if error_log.find_error(association_link.id)[1]:
                associations_links.append(association_link.puml(self.style["relationship_error"]))
            else:
                associations_links.append(association_link.puml(self.style["relationship_ok"]))

        inheritances_nodes = []
        inheritances_links = []
        for inheritance in model.inheritances:
            if error_log.find_error(inheritance.id)[1]:
                node, links = inheritance.puml(self.style["inheritance_error"], self.style["inheritance_link_error"])
            else:
                node, links = inheritance.puml(self.style["inheritance_ok"], self.style["inheritance_link_ok"])
            inheritances_nodes.append(node)
            inheritances_links.extend(links)

        packages = []
        for package in model.packages:
            if error_log.find_error(package.id)[1]:
                packages.append(package.puml(self.style["entity_error"]))
            else:
                packages.append(package.puml(self.style["package_ok"]))

        relationships = []
        for relationship in model.relationships:
            if error_log.find_error(relationship.id)[1]:
                relationships.append(relationship.puml(self.style["relationship_error"]))
            else:
                relationships.append(relationship.puml(self.style["relationship_ok"]))

        end = "@enduml"

        # write the model to a file
        with open(f"{path}", "w", encoding="utf-8") as file:
            file.write(model_str)
            file.write("\n")
            file.write(message)
            file.write("\n")
            for table in tables:
                file.write(table)
                file.write("\n")
            for association in associations:
                file.write(association)
                file.write("\n")
            for package in packages:
                file.write(package)
                file.write("\n")
            for node in inheritances_nodes:
                file.write(node)
                file.write("\n")
            for relationship in relationships:
                file.write(relationship)
                file.write("\n")
            for association_link in associations_links:
                file.write(association_link)
                file.write("\n")
            for link in inheritances_links:
                file.write(link)
                file.write("\n")
            file.write(end)

        # correct the file and process it to an image
        self.correct_file(f"{path}")
        self.process_file(f"{path}")

    def correct_file(self, path: str):
        """
                Correct the encoding of the file to cp1252, which is used by the PlantUML library.
                :param path: The path to the file to be corrected.
        """
        with open(rf'{path}', 'r', encoding='utf-8') as file:
            data = file.read()
            data = data.replace(u"\u010c", 'C')
            data = data.replace(u"\u010d", 'c')

        with open(rf'{path}', 'w', encoding='cp1252') as file:
            file.write(data)

    def process_file(self, path: str):
        """
                Process the file to an image using the PlantUML library.

                :param path: The path to the file to be processed.
        """
        if self.mode == "PNG":
            self.server.processes_file(abspath(f"{path}"))
        else:
            self.server.processes_file(abspath(f"{path}"), abspath(f"{os.path.splitext(path)[0]}.svg"))
