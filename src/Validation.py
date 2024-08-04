from typing import Set

import CDMmodel
import CDMparser
import WordMatch
import ErrorLog


class Validation:
    """
    The Validation class is used to validate the source model against the solution model.
    It uses the WordMatch class to match names in the source and solution models.
    Any errors found during the validation are logged in an instance of the ErrorLog class.
    """

    def __init__(self, src_model: CDMmodel.Model, solution_model: CDMmodel.Model):
        """
        Initialize the Validation class with a source model and a solution model.
        Also initializes a WordMatch instance and an ErrorLog instance.

        :param src_model: The source model to be validated.
        :param solution_model: The solution model to validate against.
        """
        self.solution_model: CDMmodel.Model = solution_model
        self.src_model: CDMmodel.Model = src_model
        self.name_match_threshold = 0.85
        self.wm = WordMatch.WordMatch()
        self.error_log = ErrorLog.ErrorLog()

    def validate(self):
        """
        Validate the entities, relationships, and inheritances in the source model against the solution model.
        """
        self.validate_entities()
        self.validate_relationships()
        self.validate_inheritances()
        self.validate_associations()
        self.validate_association_links()

    def validate_entities(self):
        """
                Validate the entities in the source model against the entities in the solution model.
        """
        src_entities = self.src_model.entities
        solution_entities = self.solution_model.entities

        # Create a set of solution entities to track unmatched entities
        unmatched_solution_entities = set(solution_entities)

        for src_entity in src_entities:
            # Get the most similar entity name from the solution model
            solution_entity_match, score = self.wm.compare_word(
                src_entity.name,
                [entity.name for entity in unmatched_solution_entities]
            )

            # If the score is above the threshold, try to match the entities
            if score > self.name_match_threshold:
                matching_entity = next(
                    (entity for entity in unmatched_solution_entities if entity.name == solution_entity_match),
                    None
                )
                if matching_entity:
                    unmatched_solution_entities.remove(matching_entity)
                    self.validate_entity(src_entity.id, matching_entity.id)
                else:
                    self.error_log.add_error(
                        "Entity", src_entity.id, src_entity.name, "Error",
                        f"Matching entity {solution_entity_match} not found in solution model or already matched"
                    )
            else:
                self.error_log.add_error(
                    "Entity", src_entity.id, src_entity.name, "Error",
                    f"Entity {src_entity.name} not found in solution model"
                )

        # if there are unmatched entities in the solution model, log them as errors
        if unmatched_solution_entities:
            for entity in unmatched_solution_entities:
                self.error_log.add_error(
                    "Entity", None, None, "Error",
                    f"Unmatched entity in solution model: {entity.name}"
                )

    def validate_entity(self, src_entity_id, solution_entity_id):
        """
                Validate an entity in the source model against an entity in the solution model.

                :param src_entity_id: The id of the entity in the source model.
                :param solution_entity_id: The id of the entity in the solution model.
        """
        src_entity = [entity for entity in self.src_model.entities if entity.id == src_entity_id][0]
        solution_entity = [entity for entity in self.solution_model.entities if entity.id == solution_entity_id][0]

        # check for inheritence
        if src_entity.is_child != solution_entity.is_child:
            #CORRECT THE ERROR MSG
            self.error_log.add_error("Entity", src_entity.id, src_entity.name, "Error",
                                     "Entity child property mismatch")

        self.validate_attributes(src_entity_id, solution_entity_id)
        self.validate_identifiers(src_entity_id, solution_entity_id)

    def validate_attributes(self, src_table_id, solution_table_id):
        """
                Validate the attributes of an entity in the source model against the attributes of an entity in the solution model.

                :param src_table_id: The id of the entity in the source model.
                :param solution_table_id: The id of the entity in the solution model.
        """
        # Create a set of solution attributes to track unmatched entities
        unmatched_solution_attributes: set[CDMmodel.Identifier] = set(
            self.solution_model.get_attributes(solution_table_id))

        for src_attribute in self.src_model.get_attributes(src_table_id):
            # get the most similar attribute name from the solution model
            solution_attribute_match_name, score = self.wm.compare_word(src_attribute.name,
                                                                        [attribute.name for attribute in
                                                                         unmatched_solution_attributes])

            # if the score is above the threshold, validate the attributes
            if score > self.name_match_threshold:
                matching_attribute = next(
                    (attribute for attribute in unmatched_solution_attributes if
                     attribute.name == solution_attribute_match_name),
                    None
                )

                if matching_attribute:
                    unmatched_solution_attributes.remove(matching_attribute)
                    if src_attribute.datatype != matching_attribute.datatype:
                        self.error_log.add_error("Attribute", src_table_id, src_attribute.name, "Error",
                                                 f"Attribute {src_attribute.name} datatype mismatch")

                    if src_attribute.mandatory != matching_attribute.mandatory:
                        self.error_log.add_error("Attribute", src_table_id, src_attribute.name, "Error",
                                                 f"Attribute {src_attribute.name} mandatory property mismatch")
                else:
                    self.error_log.add_error(
                        "Attribute", src_table_id, None, "Error",
                        f"Matching attribute {solution_attribute_match_name} not found in solution model or already matched"
                    )
            else:
                self.error_log.add_error("Attribute", src_table_id, src_attribute.name, "Error",
                                         f"Attribute {src_attribute.name} not found in the solution model")

        # if there are unmatched entities in the solution model, log them as errors
        if unmatched_solution_attributes:
            for attribute in unmatched_solution_attributes:
                self.error_log.add_error(
                    "Entity", src_table_id, None, "Error",
                    f"Unmatched attribute in entity {self.src_model.get_table_name_by_id(src_table_id)}: {attribute.name}"
                )

    def validate_identifier_attributes(self, src_identifier, solution_identifiers):
        """
                Validate the attributes of an identifier in the source model against the attributes of an identifier in the solution model.

                :param src_identifier: The identifier in the source model.
                :param solution_identifiers: The identifiers in the solution model.
        """
        solution_identifier_attributes = [
            [attribute.name for attribute in identifier.identifier_attributes]
            for identifier in solution_identifiers
        ]

        for src_attribute in src_identifier.identifier_attributes:
            scores = []
            for sol_attributes in solution_identifier_attributes:
                solution_attribute_match_name, score = self.wm.compare_word(src_attribute.name, sol_attributes)
                scores.append(score)
            # Check if the minimum score is below the threshold
            if min(scores) < self.name_match_threshold:
                self.error_log.add_error("Identifier", src_identifier.id, src_attribute.name, "Error",
                                         f"Identifier attributes mismatch in solution model")

                return None, False

        # If we pass all checks, return the matching identifier object and True
        for identifier in solution_identifiers:
            sol_attributes = [attribute.name for attribute in identifier.identifier_attributes]
            match_found = all(self.wm.compare_word(src_attribute.name, sol_attributes)[1] >= self.name_match_threshold
                              for src_attribute in src_identifier.identifier_attributes)
            if match_found:
                return identifier, True

        # If no matches found
        return None, False

    def validate_identifiers(self, src_table_id, solution_table_id):
        """
                Validate the identifiers of an entity in the source model against the identifiers of an entity in the solution model.
                There is no name matching for identifiers, only attribute matching.

                :param src_table_id: The id of the entity in the source model.
                :param solution_table_id: The id of the entity in the solution model.
        """
        src_identifiers = self.src_model.get_identifiers(src_table_id)
        unmatched_solution_identifiers: set[CDMmodel.Identifier] = set(
            self.solution_model.get_identifiers(solution_table_id))
        for src_identifier in src_identifiers:
            solution_identifier, flag = self.validate_identifier_attributes(src_identifier,
                                                                            unmatched_solution_identifiers)
            if flag:
                unmatched_solution_identifiers.remove(solution_identifier)
                if solution_identifier.is_primary != src_identifier.is_primary:
                    self.error_log.add_error("Identifier", src_table_id, src_identifier.id, "Error",f"Table {self.src_model.get_table_name_by_id(src_table_id)} identifier {src_identifier.name} primary property mismatch")
                    break
            #else:
                #self.error_log.add_error("Identifier", src_table_id, src_identifier.id, "Error", f"Table {self.src_model.get_table_name_by_id(src_table_id)} identifier {src_identifier.name} not found in solution model")

        if unmatched_solution_identifiers:
            for identifier in unmatched_solution_identifiers:
                self.error_log.add_error("Identifier", src_table_id, None, "Error",f"Unmatched identifier in entity {self.src_model.get_table_name_by_id(src_table_id)}: {identifier.name}")

    def validate_relationship_entities(self, src_relationship, solution_relationship):
        """
                Validate the entities of a relationship in the source model against the entities of a relationship in the solution model.

                :param src_relationship: The relationship in the source model.
                :param solution_relationship: The relationship in the solution model.
        """

        solution_entity_match, score = self.wm.compare_word(src_relationship.entity1.name,
                                                            [solution_relationship.entity1.name])
        solution_entity_match2, score2 = self.wm.compare_word(src_relationship.entity2.name,
                                                              [solution_relationship.entity2.name])

        solution_relationship_match_name, name_score = self.wm.compare_word(src_relationship.name,
                                                                            [solution_relationship.name])

        if score > self.name_match_threshold and score2 > self.name_match_threshold and name_score > self.name_match_threshold:
            return True

    def validate_relationships(self):
        """
                Validate the relationships in the source model against the relationships in the solution model.
        """
        unmatched_sol_relationships = set(self.solution_model.relationships)

        for src_relationship in self.src_model.relationships:
            for sol_relationship in unmatched_sol_relationships:
                if self.validate_relationship_entities(src_relationship, sol_relationship):
                    unmatched_sol_relationships.remove(sol_relationship)

                    if src_relationship.cardinality_1to2 != sol_relationship.cardinality_1to2 or src_relationship.cardinality_2to1 != sol_relationship.cardinality_2to1:
                        self.error_log.add_error("Relationship", src_relationship.id, src_relationship.name, "Error",
                                                 f"Relationship {src_relationship.name} cardinality mismatch")

                    if src_relationship.is_dependent_e1 != sol_relationship.is_dependent_e1 or src_relationship.is_dependent_e2 != sol_relationship.is_dependent_e2:
                        self.error_log.add_error("Relationship", src_relationship.id, src_relationship.name, "Error",
                                                 f"Relationship {src_relationship.name} dependent property mismatch")
                        break
                    else:
                        break
            else:
                self.error_log.add_error("Relationship", src_relationship.id, src_relationship.name, "Error",
                                         f"Relationship {src_relationship.name} not found in solution model")

        if unmatched_sol_relationships:
            for relationship in unmatched_sol_relationships:
                self.error_log.add_error("Relationship", None, None, "Error",
                                         f"Unmatched relationship in solution model: {relationship.name}")

    def validate_inheritance(self, src_inheritance, solution_inheritance):
        """
                Validate an inheritance in the source model against an inheritance in the solution model.

                :param src_inheritance: The inheritance in the source model.
                :param solution_inheritance: The inheritance in the solution model.
        """

        # compare the names of the inheritance and the parent entity
        parent_match, parent_score = self.wm.compare_word(src_inheritance.parent.name,
                                                          [solution_inheritance.parent.name])

        # compare the names of the children entities
        children_scores = []
        for child in src_inheritance.children:
            best_child_match, best_child_score = "", 0
            for solution_child in solution_inheritance.children:
                curr_match, curr_score = self.wm.compare_word(child.name, [solution_child.name])
                if curr_score > best_child_score:
                    best_child_match, best_child_score = curr_match, curr_score
            children_scores.append([best_child_match, best_child_score])

        if any(x[1] < self.name_match_threshold for x in children_scores):
            error_info = ["Inheritance", src_inheritance.id, src_inheritance.name, "Error",
                          f"Inheritance {src_inheritance.name} children mismatch"]
            return error_info, False

        if parent_score < self.name_match_threshold:
            error_info = ["Inheritance", src_inheritance.id, src_inheritance.name, "Error",
                          f"Inheritance {src_inheritance.name} parent mismatch"]
            return error_info, False

        if src_inheritance.mutually_exclusive != solution_inheritance.mutually_exclusive:
            self.error_log.add_error("Inheritance", src_inheritance.id, src_inheritance.name, "Error",
                                     f"Inheritance {src_inheritance.name} mutually exclusive property mismatch")
            return None, True

        if src_inheritance.complete != solution_inheritance.complete:
            self.error_log.add_error("Inheritance", src_inheritance.id, src_inheritance.name, "Error",
                                     f"Inheritance {src_inheritance.name} complete property mismatch")
            return None, True

        return None, True

    def validate_inheritances(self):
        """
                Validate the inheritances in the source model against the inheritances in the solution model.
        """
        unmatched_sol_inheritances = set(self.solution_model.inheritances)
        for src_inheritance in self.src_model.inheritances:
            for sol_inheritance in unmatched_sol_inheritances:
                err_info, flag = self.validate_inheritance(src_inheritance, sol_inheritance)
                if flag:
                    unmatched_sol_inheritances.remove(sol_inheritance)
                    break
            else:
                if err_info:
                    self.error_log.add_error(*err_info)

                else:
                    self.error_log.add_error("Inheritance", src_inheritance.id, src_inheritance.name, "Error",
                                             f"Inheritance {src_inheritance.name} not found in solution model")

        if unmatched_sol_inheritances:
            for inheritance in unmatched_sol_inheritances:
                self.error_log.add_error("Inheritance", None, None, "Error",
                                         f"Unmatched inheritance in solution model: {inheritance.name}")

    def validate_association(self, src_association, solution_association):
        """
                Validate an association in the source model against an association in the solution model.

                :param src_association: The association in the source model.
                :param solution_association: The association in the solution model.
        """
        if len(src_association.attributes) == len(solution_association.attributes) and len(
                src_association.attributes) == 0:
            return True

        attribute_scores = []
        for src_attribute in src_association.attributes:
            # get the most similar attribute name from the solution model
            for solution_attribute in solution_association.attributes:
                solution_attribute_match_name, score = self.wm.compare_word(src_attribute.name,
                                                                            [solution_attribute.name])
                attribute_scores.append([score, src_attribute.name])

        if all(x[0] < self.name_match_threshold for x in attribute_scores):
            self.error_log.add_error("Association", src_association.id, src_association.name, "Error",
                                     f"Association attributes mismatch")

            return False

    def validate_associations(self):
        """
                Validate the associations in the source model against the associations in the solution model.
        """
        src_entity_associations = self.src_model.associations
        solution_entity_associations = set(self.solution_model.associations)

        for src_entity_association in src_entity_associations:
            for solution_entity_association in solution_entity_associations:
                name_match, name_score = self.wm.compare_word(src_entity_association.name,
                                                              [solution_entity_association.name])
                if name_score > self.name_match_threshold:
                    if self.validate_association(src_entity_association, solution_entity_association):
                        solution_entity_associations.remove(solution_entity_association)
                        break
            else:
                self.error_log.add_error("Association", src_entity_association.id, src_entity_association.name, "Error",
                                         f"Association {src_entity_association.name} not found in solution model")
        if solution_entity_associations:
            for association in solution_entity_associations:
                self.error_log.add_error("Association", None, None, "Error",
                                         f"Unmatched association in solution model: {association.name}")

    def validate_association_link(self, src_link, solution_link):
        """
                Validate an association link in the source model against an association link in the solution model.

                :param src_link: The association link in the source model.
                :param solution_link: The association link in the solution model.
        """
        solution_entity_match, score = self.wm.compare_word(src_link.association.name, [solution_link.association.name])
        solution_entity_match2, score2 = self.wm.compare_word(src_link.entity.name, [solution_link.entity.name])
        if score > self.name_match_threshold and score2 > self.name_match_threshold:
            return True
        return False

    def validate_association_links(self):
        """
                Validate the association links in the source model against the association links in the solution model.
        """
        src_links = self.src_model.association_links
        solution_links = set(self.solution_model.association_links)

        for src_link in src_links:
            for solution_link in solution_links:
                # validate the association link entities and cardinality
                if self.validate_association_link(src_link, solution_link):
                    solution_links.remove(solution_link)
                    if src_link.cardinality == solution_link.cardinality:
                        break
                    else:
                        self.error_log.add_error("Association Link", src_link.id, src_link.association, "Error",
                                                 f"Association link {src_link.association, src_link.entity} cardinality mismatch")

            else:
                self.error_log.add_error("Association Link", src_link.id, src_link.association, "Error",
                                         f"Association link {src_link.association, src_link.entity} not found in solution model")

        if solution_links:
            for link in solution_links:
                self.error_log.add_error("Association Link", None, None, "Error",
                                         f"Unmatched association link in solution model: {link.association, link.entity}")


if __name__ == '__main__':
    import time

    t = time.process_time()
    model = CDMparser.CDMParser("W:/Diplomsko delo/Diploma/tests/conceptual_tasks/video_shop/solution.cdm")
    model2 = CDMparser.CDMParser("W:/Diplomsko delo/Diploma/tests/conceptual_tasks/video_shop/Primer 8.cdm")
    validation = Validation(model.get_main_model(), model2.get_main_model())
    validation.validate()
    validation.error_log.prt()
    elapsed_time = time.process_time() - t
    print("Time:", elapsed_time, "seconds")
