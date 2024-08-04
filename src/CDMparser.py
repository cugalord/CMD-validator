import xml.etree.ElementTree as     ET
import re
import CDMmodel

'''
CDMParser class reads the input cdm file, extracts the necessary information and returns it in class object form <- CDMmodel.py
'''


class CDMParser:
    """
    The CDMParser class is used to parse the input CDM file and extract the necessary information.
    It returns the information in the form of a CDMmodel object.
    """

    def __init__(self, path: str):
        self.path = path
        self.namespaces = {
            'a': 'attribute',
            'c': 'collection',
            'o': 'object',
        }
        try:
            self.tree = ET.parse(self.path)
            self.root = self.tree.getroot()
        except Exception as e:
            print("E:", e)

    def link_inheritances(self, entities: list[CDMmodel.Entity], inheritances: list[CDMmodel.Inheritance]):
        """
                Link the inheritances to their respective entities based on the 'ref' attribute.
                Also adds an 'is_child' attribute to the child entity.

                :param entities: The list of entities in the model.
                :param inheritances: The list of inheritances in the model.
        """
        for inheritance in inheritances:
            inheritance.parent = [entity for entity in entities if entity.id == inheritance.parent][0]
            children = []
            for child in inheritance.children:
                for entity in entities:
                    if entity.id == child:
                        entity.is_child = True
                        children.append(entity)
            inheritance.children = children

    def link_domains(self, entities: list[CDMmodel.Entity], domains: list[CDMmodel.Domain]):
        """
                Link the domains to their respective entity attributes based on the 'ref' attribute.

                :param entities: The list of entities in the model.
                :param domains: The list of domains in the model.
        """
        for entity in entities:
            for attribute in entity.attributes:
                if attribute.domain is not None:
                    attribute.domain = [domain for domain in domains if domain.id == attribute.domain][0]

    def link_relationships(self, entities: list[CDMmodel.Entity], relationships: list[CDMmodel.Relationship]):
        """
                Link the relationships to their respective entities based on the 'ref' attribute.

                :param entities: The list of entities in the model.
                :param relationships: The list of relationships in the model.
        """
        for relationship in relationships:
            relationship.entity1 = [entity for entity in entities if entity.id == relationship.entity1][0]
            relationship.entity2 = [entity for entity in entities if entity.id == relationship.entity2][0]
            relationship.entity1.relationships.append(relationship)
            relationship.entity2.relationships.append(relationship)

    def link_association_links(self, entities: list[CDMmodel.Entity], associations: list[CDMmodel.Association],
                               association_links: list[CDMmodel.AssociationLink]):
        """
               Link the association links to their respective associations and entities based on the 'ref' attribute.

               :param entities: The list of entities in the model.
               :param associations: The list of associations in the model.
               :param association_links: The list of association links in the model.
       """
        for association_link in association_links:
            association_link.association = \
                [association for association in associations if association.id == association_link.association][0]
            association_link.entity = [entity for entity in entities if entity.id == association_link.entity][0]
            association_link.entity.association_links.append(association_link)
            association_link.association.association_links.append(association_link)

    def link_attributes(self, identifiers: list[CDMmodel.Identifier], attributes: list[CDMmodel.Attribute]):
        """
              Link the attributes to their respective identifiers based on the 'ref' attribute.

              :param identifiers: The list of identifiers in the model.
              :param attributes: The list of attributes in the model.
        """
        for identifier in identifiers:
            identifier.identifier_attributes = [attribute for attribute in attributes if
                                                attribute.id in identifier.identifier_attributes]

    def resolve_domain(self, domain: ET.Element) -> CDMmodel.Domain:
        """
                Resolve a domain element into a Domain object.

                :param domain: The domain element to be resolved.
                :return: The resolved Domain object.
        """
        id = domain.attrib['Id']
        name = domain.find("./a:Name", self.namespaces).text
        code = domain.find("./a:Code", self.namespaces).text
        datatype = re.sub("[0-9]|[0-9,0-9]", '', domain.find("./a:DataType", self.namespaces).text)
        length = domain.find("./a:Length", self.namespaces).text if domain.find("./a:Length",
                                                                                self.namespaces) is not None else None
        precision = domain.find("./a:Precision", self.namespaces).text if domain.find("./a:Precision",
                                                                                      self.namespaces) is not None else None

        return CDMmodel.Domain(id, name, code, datatype, length, precision)

    def resolve_entity_identifiers(self, entity: ET.Element) -> list[CDMmodel.Identifier]:
        """
               Resolve the identifiers of an entity element into a list of Identifier objects.

               :param entity: The entity element whose identifiers are to be resolved.
               :return: The list of resolved Identifier objects.
        """
        if entity.find("./c:Identifiers", self.namespaces) is None:
            return []  # return empty list

        identifiers = []
        for identifier in entity.find("./c:Identifiers", self.namespaces):
            identifierID = identifier.attrib['Id']
            name = identifier.find("./a:Name", self.namespaces).text

            if identifier.find("./c:Identifier.Attributes", self.namespaces) is not None:
                identifier_attributes = [attribute.attrib['Ref'] for attribute in
                                         identifier.find("./c:Identifier.Attributes", self.namespaces)]
            else:
                identifier_attributes = []

            primary_identifier = True if identifierID == \
                                         entity.find("./c:PrimaryIdentifier/o:Identifier",
                                                     self.namespaces).attrib['Ref'] else False
            identifiers.append(CDMmodel.Identifier(identifierID, name, identifier_attributes, primary_identifier))

        return identifiers

    def resolve_data_item(self, model: ET.Element, data_item_id: str) -> dict:
        """
                Resolve a data item element into a dictionary of data item data.

                :param model: The model element that contains the data item.
                :param data_item_id: The id of the data item to be resolved.
                :return: The dictionary of resolved data item data.
        """
        data_item = model.find(f"./c:DataItems/o:DataItem[@Id='{data_item_id}']", self.namespaces)
        data_item_data = dict()

        data_item_data["dataItemID"] = data_item.attrib['Id']
        data_item_data["objectID"] = data_item.find("./a:ObjectID", self.namespaces).text
        data_item_data["name"] = data_item.find("./a:Name", self.namespaces).text
        data_item_data["code"] = data_item.find("./a:Code", self.namespaces).text
        data_item_data["datatype"] = re.sub("[0-9]|[0-9,0-9]", '',
                                            data_item.find("./a:DataType", self.namespaces).text) if data_item.find(
            "./a:DataType", self.namespaces) is not None else None
        data_item_data["length"] = data_item.find("./a:Length", self.namespaces).text if data_item.find("./a:Length",
                                                                                                        self.namespaces) is not None else None
        data_item_data["precision"] = data_item.find("./a:Precision", self.namespaces).text if data_item.find(
            "./a:Precision", self.namespaces) is not None else None
        data_item_data["domain"] = data_item.find("./c:Domain/o:Domain", self.namespaces).attrib[
            'Ref'] if data_item.find("./c:Domain", self.namespaces) is not None else None
        return data_item_data

    def resolve_attributes(self, model: ET.Element, entity: ET.Element) -> list[CDMmodel.Attribute]:
        """
                Resolve the attributes of an entity element into a list of Attribute objects.

                :param model: The model element that contains the entity.
                :param entity: The entity element whose attributes are to be resolved.
                :return: The list of resolved Attribute objects.
        """
        if entity.find("./c:Attributes", self.namespaces) is None:
            return []

        attributes = []
        for attribute in entity.find("./c:Attributes", self.namespaces):
            attributeID = attribute.attrib['Id']
            mandatory = True if attribute.find("./a:BaseAttribute.Mandatory", self.namespaces) is not None else False
            DataItem = self.resolve_data_item(model,
                                              attribute.find("./c:DataItem/o:DataItem", self.namespaces).attrib[
                                                  'Ref']) if attribute.find(
                "./c:DataItem/o:DataItem", self.namespaces) is not None else None
            attributes.append(
                CDMmodel.Attribute(attributeID, DataItem["name"], DataItem["code"], mandatory, DataItem["domain"],
                                   DataItem["datatype"], DataItem["length"], DataItem["precision"]))
        return attributes

    def resolve_entity(self, model: ET.Element, entity: ET.Element) -> CDMmodel.Entity:
        """
                Resolve an entity element into an Entity object.

                :param model: The model element that contains the entity.
                :param entity: The entity element to be resolved.
                :return: The resolved Entity object.
        """
        id = entity.attrib['Id']
        name = entity.find("./a:Name", self.namespaces).text
        code = entity.find("./a:Code", self.namespaces).text

        identifiers = self.resolve_entity_identifiers(entity)
        attributes = self.resolve_attributes(model, entity)
        self.link_attributes(identifiers, attributes)

        return CDMmodel.Entity(id, name, code, attributes, identifiers)

    def resolve_relationship(self, relationship: ET.Element) -> CDMmodel.Relationship:
        """
               Resolve a relationship element into a Relationship object.

               :param relationship: The relationship element to be resolved.
               :return: The resolved Relationship object.
       """
        id = relationship.attrib['Id']
        name = relationship.find("./a:Name", self.namespaces).text
        code = relationship.find("./a:Code", self.namespaces).text
        dependent_e1 = False
        dependent_e2 = False
        if relationship.find("./a:DependentRole", self.namespaces) is not None:
            # if A is dependent_e1 is True, else (is B) -> dependent_e2 is True
            if relationship.find("./a:DependentRole", self.namespaces).text == 'A':
                dependent_e1 = True
            else:
                dependent_e2 = True

        cardinality_1to2 = relationship.find("./a:Entity1ToEntity2RoleCardinality", self.namespaces).text
        cardinality_2to1 = relationship.find("./a:Entity2ToEntity1RoleCardinality", self.namespaces).text
        entity1_ref = relationship.find("./c:Object1/o:Entity", self.namespaces).attrib['Ref']
        entity2_ref = relationship.find("./c:Object2/o:Entity", self.namespaces).attrib['Ref']

        return CDMmodel.Relationship(id, name, code,dependent_e1, dependent_e2, entity1_ref, entity2_ref, cardinality_1to2, cardinality_2to1)

    def resolve_association(self, model: ET.Element, association: ET.Element) -> CDMmodel.Association:
        """
               Resolve an association element into an Association object.

               :param model: The model element that contains the association.
               :param association: The association element to be resolved.
               :return: The resolved Association object.
        """
        id = association.attrib['Id']
        name = association.find("./a:Name", self.namespaces).text
        code = association.find("./a:Code", self.namespaces).text

        attributes = self.resolve_attributes(model, association)

        return CDMmodel.Association(id, name, code, attributes)

    def get_entities(self, model: ET.Element) -> list[CDMmodel.Entity]:
        """
                Get a list of Entity objects from a model element.

                :param model: The model element from which to get the entities.
                :return: The list of Entity objects.
        """
        entities = model.findall("./c:Entities/", self.namespaces)
        if entities is None or len(entities) == 0:
            return []
        return [self.resolve_entity(model, entity) for entity in entities]

    def get_relationships(self, model: ET.Element) -> list[CDMmodel.Relationship]:
        """
                Get a list of Relationship objects from a model element.

                :param model: The model element from which to get the relationships.
                :return: The list of Relationship objects.
        """
        relationships = model.findall("./c:Relationships/", self.namespaces)
        return [self.resolve_relationship(relationship) for relationship in relationships]

    def get_domains(self, model: ET.Element) -> list[CDMmodel.Domain]:
        """
                Get a list of Domain objects from a model element.

                :param model: The model element from which to get the domains.
                :return: The list of Domain objects.
        """
        domains = model.findall("./c:Domains/", self.namespaces)
        return [self.resolve_domain(domain) for domain in domains]

    def get_associations(self, model: ET.Element) -> list[CDMmodel.Association]:
        """
               Get a list of Association objects from a model element.

               :param model: The model element from which to get the associations.
               :return: The list of Association objects.
        """
        associations = model.findall("./c:Associations/", self.namespaces)
        return [self.resolve_association(model, association) for association in associations]

    def resolve_association_link(self, association_link: ET.Element) -> CDMmodel.AssociationLink:
        """
                Resolve an association link element into an AssociationLink object.

                :param association_link: The association link element to be resolved.
                :return: The resolved AssociationLink object.
        """

        id = association_link.attrib['Id']
        cardinality = association_link.find("./a:Cardinality", self.namespaces).text
        association_ref = association_link.find("./c:Object1/o:Association", self.namespaces).attrib['Ref']
        entity_ref = association_link.find("./c:Object2/o:Entity", self.namespaces).attrib['Ref']

        return CDMmodel.AssociationLink(id, association_ref, entity_ref, cardinality)

    def get_association_links(self, model: ET.Element) -> list[CDMmodel.AssociationLink]:
        """
                Get a list of AssociationLink objects from a model element.

                :param model: The model element from which to get the association links.
                :return: The list of AssociationLink objects.
        """
        association_links = model.findall("./c:AssociationsLinks/", self.namespaces)
        return [self.resolve_association_link(association_link) for association_link in association_links]

    def resolve_inheritance_links(self, model: ET.Element, inheritance_id: str) -> list:
        """
                Resolve the inheritance links of an inheritance element into a list of children references.

                :param model: The model element that contains the inheritance.
                :param inheritance_id: The id of the inheritance whose links are to be resolved.
                :return: The list of children references.
        """
        inheritance_links = model.findall(f"./c:InheritanceLinks/", self.namespaces)
        children_refs = []
        for link in inheritance_links:
            if link.find(f"./c:Object1/o:Inheritance", self.namespaces).attrib['Ref'] == inheritance_id:
                children_refs.append(link.find(f"./c:Object2/o:Entity", self.namespaces).attrib['Ref'])
        return children_refs

    def resolve_inheritance(self, model: ET.Element, inheritance: ET.Element) -> CDMmodel.Inheritance:
        """
                Resolve an inheritance element into an Inheritance object.

                :param model: The model element that contains the inheritance.
                :param inheritance: The inheritance element to be resolved.
                :return: The resolved Inheritance object.
        """
        id = inheritance.attrib['Id']
        name = inheritance.find("./a:Name", self.namespaces).text
        code = inheritance.find("./a:Code", self.namespaces).text
        mutually_exclusive = False if inheritance.find("./a:MutuallyExclusive", self.namespaces) is None else True
        complete = False if inheritance.find("./a:Inheritance.Complete", self.namespaces) is None else True
        parent_ref = inheritance.find("./c:ParentEntity/o:Entity", self.namespaces).attrib['Ref']
        children_refs = self.resolve_inheritance_links(model, id)

        return CDMmodel.Inheritance(id, name, code, mutually_exclusive, complete, parent_ref, children_refs)

    def get_inheritances(self, model: ET.Element) -> list[CDMmodel.Inheritance]:
        """
                Resolve an inheritance element into an Inheritance object.

                :param model: The model element that contains the inheritance.
                :param inheritance: The inheritance element to be resolved.
                :return: The resolved Inheritance object.
        """
        inheritances = model.findall("./c:Inheritances/", self.namespaces)
        return [self.resolve_inheritance(model, inheritance) for inheritance in inheritances]

    def get_packages(self, model) -> list[CDMmodel.Package]:
        """
                Get a list of Package objects from a model element.

                :param model: The model element from which to get the packages.
                :return: The list of Package objects.
        """
        packages = model.findall("./c:Packages/", self.namespaces)
        return_packages = []
        for package in packages:
            id = package.attrib['Id']
            name = package.find("./a:Name", self.namespaces).text
            code = package.find("./a:Code", self.namespaces).text

            domains = self.get_domains(package)
            entities = self.get_entities(package)
            relationships = self.get_relationships(package)
            inheritances = self.get_inheritances(package)

            associations = self.get_associations(package)
            association_links = self.get_association_links(package)

            self.link_association_links(entities, associations, association_links)
            self.link_relationships(entities, relationships)
            self.link_domains(entities, domains)
            self.link_inheritances(entities, inheritances)
            return_packages.append(
                CDMmodel.Package(id, name, code, entities, inheritances, relationships, associations, association_links,
                                 domains))
        return return_packages

        # returns a model object

    def get_main_model(self) -> CDMmodel.Model:
        """
                Get the main Model object from the root of the CDM file.

                :return: The main Model object.
        """
        main_model = self.root.findall("./o:RootObject/c:Children/o:Model", self.namespaces)[0]
        id = main_model.attrib['Id']
        name = main_model.find("./a:Name", self.namespaces).text
        code = main_model.find("./a:Code", self.namespaces).text

        domains = self.get_domains(main_model)
        entities = self.get_entities(main_model)
        relationships = self.get_relationships(main_model)
        inheritances = self.get_inheritances(main_model)
        packages = self.get_packages(main_model)

        associations = self.get_associations(main_model)
        association_links = self.get_association_links(main_model)

        self.link_association_links(entities, associations, association_links)
        self.link_relationships(entities, relationships)
        self.link_domains(entities, domains)
        self.link_inheritances(entities, inheritances)

        return CDMmodel.Model(id, name, code, entities, inheritances, relationships, associations, association_links,
                              domains, packages)


if __name__ == '__main__':
    xml = CDMParser('W:/Diplomsko delo/Diploma/tests/conceptual_tasks/faculty/faculty_test.cdm')
    model = xml.get_main_model()
    for relationship in model.relationships:
        print(relationship)
